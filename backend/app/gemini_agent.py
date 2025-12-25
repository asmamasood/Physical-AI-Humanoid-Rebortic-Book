"""
Gemini LLM agent for RAG Chatboard.

Provides answer generation with carefully constructed system prompts
for both RAG-based and selective (context-only) chat modes.
"""

import re
import asyncio
import inspect
import logging
from typing import List, Tuple, Dict, Any, Optional
from functools import lru_cache

from google import genai
from google.genai import types as genai_types

from .config import get_settings
from .models import Citation
from .skills.registry import registry
from .skills import book_logic  # Registers book skills
from .gamification.points import points_manager

logger = logging.getLogger(__name__)


# =============================================================================
# System Prompts
# =============================================================================

SYSTEM_PROMPT_RAG = """You are a warm, human-like AI tutor for the "Physical AI & Humanoid Robotics" book.

{agent_persona}

CORE PHILOSOPHY:
- **Soft-Coded Intent**: Deeply understand the user's query intent. Adapt your response style dynamically:
  - Story request → Narrative summary with engaging flow
  - Technical question → Detailed scientific explanation with examples
  - Simple definition → Clear, concise teaching approach
  - Conversational → Friendly, encouraging tone
- **Human Tone**: Speak like a person, not a machine. Use natural phrases:
  - "I found this interesting part..."
  - "Let me help you understand..."
  - "The book explains this really well..."
  - "This is a fascinating topic!"
- **Context Strictness**: You are a specialist on THIS BOOK ONLY.
  - Answer questions based STRICTLY on the provided CONTEXT CHUNKS.
  - If the answer is not in the context, say: "I'm sorry, I couldn't find information about that in the book."
  - Do not provide general knowledge answers unless they are supported by the book context.
  - Stay grounded in the book content at all times

{profile}
{gamification}

RULES:
1. **Dynamic Response Schema**: Analyze query intent and respond accordingly:
   - Summary → Structured overview with bullet points and emojis 📖
   - Quiz → Interactive questions with clear formatting 🎯
   - Explanation → Detailed breakdown with examples and analogies
   - Chat → Natural conversation with encouragement and support
2. **Language Adaptation**:
   - Detect user language preference from query or profile
   - If user asks in Urdu or profile indicates Urdu → respond in Urdu
   - Otherwise → respond in English
   - Maintain warm tutor persona in both languages
3. **Gamification Awareness**:
   - If points/level provided, acknowledge naturally when relevant
   - Examples: "Great progress at Level 5! 🎉" or "You're doing amazing!"
   - Keep it subtle and encouraging, never robotic
4. **Citations**:
   - Always cite sources: [module:chapter:chunk_id]
   - Make citations a natural part of text flow
   - Example: "According to [module-1:intro:chunk1], Physical AI..."
5. **Uncertainty Handling**:
   - If content doesn't cover topic: "I couldn't find that specific detail in the book."
   - Suggest alternative questions or related topics when helpful
   - Be honest and transparent about limitations

CONVERSATION HISTORY:
{history}

CONTEXT CHUNKS (Book Content):
{context}

USER QUERY: {query}

(Respond warmly and naturally, adapting to the user's intent. Be helpful, encouraging, and grounded in the book content):"""


SYSTEM_PROMPT_SELECTIVE = """You are a warm, human-like AI tutor 📘😊 helping a student understand a specific highlighted section.

Your task is to answer the USER QUESTION based ONLY on the "SELECTED TEXT" below.

STRICT CONTEXT RULES:
1. Respond ONLY using information from the "SELECTED TEXT".
2. If the answer is not in the text, respond with EXACTLY: "I couldn’t find this in the selected text."
3. Be friendly and polite.

SELECTED TEXT:
\"\"\"{selection_text}\"\"\"

USER QUESTION: {query}

(Reply in a warm, human tone, using ONLY the selected text above):"""


SYSTEM_PROMPT_SUMMARY = """You are a master educator 📖✨ creating comprehensive, structured summaries of book content.

Your task is to generate a clear, engaging summary based STRICTLY on the provided CONTEXT.

SUMMARY STRUCTURE:
Use this format for your summary:

🎯 **Key Topics**
• [List main topics covered]
• [Use bullet points]
• [Be concise but informative]

📚 **Core Concepts**
1. [First major concept with brief explanation]
2. [Second major concept with brief explanation]
3. [Continue as needed]

💡 **Important Takeaways**
• [Key insight or practical application]
• [What learners should remember]
• [Why this matters]

RULES:
1. **Ground in Context**: Use ONLY the provided content below
   - Never add external knowledge or assumptions
   - If content is insufficient, state clearly: "The available content covers..."
2. **Structure & Format**:
   - Always use the 3-section structure above (Topics, Concepts, Takeaways)
   - Use emojis to make sections visually distinct
   - Keep bullet points concise (1-2 sentences max)
3. **Tone**:
   - Friendly and encouraging
   - Academic but accessible
   - Enthusiastic about the content
4. **Length**:
   - Aim for comprehensive but digestible
   - 150-300 words is ideal
   - Adjust based on content available

CONTEXT (Book Content):
{context}

USER REQUEST: {query}

(Generate a warm, structured summary that helps learners grasp the key ideas):"""


SYSTEM_PROMPT_QUIZ = """You are a friendly examiner 🎯📝 creating educational quizzes to help learners test their understanding.

Your task is to generate a moderate-difficulty quiz based STRICTLY on the provided CONTEXT.

QUIZ FORMAT:
Generate 3-5 questions using this structure:

**Question 1** (Multiple Choice)
[Clear, specific question based on the content]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]

**Answer**: [Correct letter] - [Brief explanation why this is correct and what concept it tests]

---

**Question 2** (Short Answer)
[Open-ended question requiring understanding, not just recall]

**Answer**: [Key points that should be included in a good answer]

---

[Continue with variety of question types]

QUIZ RULES:
1. **Content Grounding**:
   - Base ALL questions strictly on the provided CONTEXT
   - Never use external knowledge or assumptions
   - If content is insufficient for 3 questions, create fewer and note: "This covers the available content."
2. **Question Variety**:
   - Mix Multiple Choice and Short Answer questions
   - Include both recall (facts) and understanding (concepts) questions
   - Make at least one question application-based if possible
3. **Difficulty Level**:
   - Moderate difficulty (not too easy, not expert-level)
   - Should test understanding, not just memorization
   - Avoid trick questions or overly complex wording
4. **Answer Explanations**:
   - Always explain WHY the correct answer is right
   - For MCQs, briefly mention what concept it tests
   - For short answers, provide key points to look for
5. **Tone**:
   - Encouraging: "Let's test your understanding! 🎯"
   - Educational: Focus on learning, not just testing
   - Clear: No ambiguous or confusing questions

CONTEXT (Book Content):
{context}

USER REQUEST: {query}

(Generate an engaging, educational quiz that reinforces learning):"""


class GeminiAgent:
    """
    Async wrapper for Google Gemini API with specialized prompts.
    """
    
    def __init__(self, api_key: str = None, model_name: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (uses settings if not provided)
            model_name: Gemini model to use (uses settings if not provided)
        """
        settings = get_settings()
        
        if api_key is None:
            api_key = settings.gemini_api_key
            
        if model_name is None:
            model_name = settings.gemini_model_name
        
        # New SDK: Create client instead of configure
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        logger.info(f"GeminiAgent initialized with model: {model_name}")
    
    async def generate_rag_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        history: List[Dict[str, Any]] = [],
        user_profile: Optional[Dict[str, Any]] = None,
        gamification_status: Optional[Dict[str, Any]] = None,
        subagent: Optional[Dict[str, Any]] = None,
        selected_text: Optional[str] = None
    ) -> Tuple[str, List[Citation]]:
        """
        Generate an answer using intent detection and specialized prompts.
        """
        # 0. Early Exit if no chunks (unless Selective mode)
        intent = self._detect_intent(query, selected_text)
        if not chunks and intent != "SELECTED":
             return "Hello! 😊 I couldn't find any relevant information in the book regarding that topics. Could you try rephrasing? 📘", []
        
        logger.info(f"Detected intent: {intent}")
        
        # 2. Format Context
        context_parts = []
        for chunk in chunks:
            # Escape braces to avoid .format() errors
            safe_content = chunk['content'].replace("{", "{{").replace("}", "}}")
            context_parts.append(
                f"[{chunk['module']}:{chunk['chapter']}:{chunk['chunk_id']}]\n{safe_content}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # 3. Format Personas & Profile
        profile_text = self._format_profile(user_profile)
        gamification_text = self._format_gamification(gamification_status)
        agent_persona_text = self._format_subagent(subagent)
        
        # 4. Handle History
        history_parts = []
        for msg in history:
            h_q = msg['query'].replace("{", "{{").replace("}", "}}")
            h_r = msg['response'].replace("{", "{{").replace("}", "}}")
            history_parts.append(f"User: {h_q}\nAI: {h_r}")
        history_text = "\n\n".join(history_parts) if history_parts else "No previous history."

        # Escape current input too
        safe_query = query.replace("{", "{{").replace("}", "}}")
        safe_selection = (selected_text or "").replace("{", "{{").replace("}", "}}")

        # 5. Build Final Prompt based on Intent
        if intent == "SELECTED":
            prompt = SYSTEM_PROMPT_SELECTIVE.format(
                selection_text=safe_selection,
                query=safe_query
            )
        elif intent == "SUMMARY":
            prompt = SYSTEM_PROMPT_SUMMARY.format(
                context=context,
                query=safe_query
            )
        elif intent == "QUIZ":
            prompt = SYSTEM_PROMPT_QUIZ.format(
                context=context,
                query=safe_query
            )
        else:
            prompt = SYSTEM_PROMPT_RAG.format(
                history=history_text,
                context=context,
                profile=profile_text,
                gamification=gamification_text,
                agent_persona=agent_persona_text,
                query=safe_query
            )

        # 6. Generate
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
        )
        
        try:
            answer_text = response.text
        except Exception:
            try:
                answer_text = response.candidates[0].content.parts[0].text
            except Exception:
                answer_text = "I encountered an issue generating a response. Please try again."
        
        # 7. Post-process
        if intent == "SELECTED" and "I couldn’t find this in the selected text" in answer_text:
            return answer_text, []
            
        citations = self._extract_citations(answer_text, chunks)
        return self._add_greetings(answer_text), citations

    def _detect_intent(self, query: str, selected_text: Optional[str]) -> str:
        """
        Enhanced intent detection with priority ordering and comprehensive keyword matching.

        Returns: "SELECTED" | "SUMMARY" | "QUIZ" | "QA"
        """
        q = query.lower()

        # Priority 1: Selected Text Mode (if text provided)
        if selected_text and len(selected_text) > 10:
            logger.info("Intent: SELECTED (selected_text provided)")
            return "SELECTED"

        # Priority 2: Summary Request
        summary_keywords = [
            "summarize", "summary", "gist", "brief",
            "overview", "recap", "in short", "tldr",
            "sum up", "main points", "key points"
        ]
        if any(word in q for word in summary_keywords):
            logger.info("Intent: SUMMARY (keyword match)")
            return "SUMMARY"

        # Priority 3: Quiz/Test Request
        quiz_keywords = [
            "quiz", "test me", "questions", "assessment",
            "exam", "evaluate", "check my knowledge",
            "questionnaire", "practice questions"
        ]
        if any(word in q for word in quiz_keywords):
            logger.info("Intent: QUIZ (keyword match)")
            return "QUIZ"

        # Priority 4: Explanation/Definition Request (QA with emphasis)
        explain_keywords = [
            "explain", "define", "what is", "what are",
            "how does", "why does", "describe", "tell me about"
        ]
        if any(word in q for word in explain_keywords):
            logger.info("Intent: QA (explanation focus)")
            return "QA"

        # Default: Standard QA Mode
        logger.info("Intent: QA (default)")
        return "QA"

    def _add_greetings(self, text: str) -> str:
        """
        Add context-aware greetings based on response type.

        Detects the type of response and adds an appropriate friendly greeting.
        """
        # Check if greeting already exists (first 50 chars)
        first_line = text[:50].lower()
        if any(word in first_line for word in ["hello", "hi ", "hey", "greetings", "welcome"]):
            return text

        # Context-aware greeting selection
        text_preview = text[:100].lower()

        # Summary responses
        if any(word in text_preview for word in ["summary", "overview", "key topics", "main points"]):
            return f"Hello! 📖 Here's a summary for you:\n\n{text}"

        # Quiz responses
        if any(word in text_preview for word in ["quiz", "question", "test", "answer:"]):
            return f"Hi there! 🎯 Let's test your knowledge:\n\n{text}"

        # Not found / Uncertainty responses
        if any(phrase in text.lower() for phrase in ["couldn't find", "not found", "don't have", "unable to"]):
            return f"Hello! 😊 {text}"

        # Default friendly greeting
        return f"Hello! 😊 {text}"

    def _format_profile(self, profile: Optional[Dict]) -> str:
        if not profile: return ""
        return f"LEARNER PROFILE:\n- Expertise: {profile.get('software_role')} ({profile.get('software_level')})\n- Hardware: {profile.get('hardware_type')}\n"

    def _format_gamification(self, status: Optional[Dict]) -> str:
        if not status: return ""
        return f"GAMIFICATION:\n- Level: {status.get('level', 1)}\n- Points: {status.get('points_total', 0)}\n"

    def _format_subagent(self, subagent: Optional[Dict]) -> str:
        if not subagent: return ""
        res = f"PERSONA: {subagent.get('name')}\n"
        skills = subagent.get('skills', [])
        if skills:
            res += "Skills: " + ", ".join([s['name'] for s in skills]) + "\n"
        return res

    async def generate_selective_answer(
        self,
        query: str,
        selection_text: str
    ) -> str:
        """
        Generate an answer based ONLY on the selected text.
        """
        # Build prompt
        prompt = SYSTEM_PROMPT_SELECTIVE.format(
            selection_text=selection_text,
            query=query
        )
        
        # Generate response
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
        )
        
        return response.text.strip()

    async def generate_smart_answer(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        AI-powered answer generation with Skill awareness (Tool Calling).
        
        If Gemini identifies a skill usage, it will be executed and rewarded.
        """
        # Get all registered skills for Gemini
        tools = registry.get_all_tool_definitions()
        
        # Create chat session with tools
        config = genai_types.GenerateContentConfig(
            tools=tools if tools else None
        )
        
        chat = self.client.chats.create(
            model=self.model_name,
            config=config
        )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: chat.send_message(contents=query)
            )
            
            # Handle Potential Function Calls
            if not response.candidates or not response.candidates[0].content.parts:
                return "I'm sorry, I couldn't generate a response. Please try rephrasing."
                
            part = response.candidates[0].content.parts[0]
            
            # Use hasattr check for function_call as it's safer in some SDK versions
            if hasattr(part, "function_call") and part.function_call:
                call = part.function_call
                skill_func = registry.get_skill(call.name)
                
                if skill_func:
                    # Execute the skill
                    args = dict(call.args)
                    
                    if "user_id" in inspect.signature(skill_func).parameters and user_id:
                        args["user_id"] = user_id
                    
                    try:
                        result = await skill_func(**args)
                        
                        if user_id:
                            await points_manager.award_points(user_id, "use_skill")
                        
                        # Send result back to AI to finalize answer
                        # Send function response back to model
                        function_response_part = genai_types.Part.from_function_response(
                            name=call.name,
                            response={"result": result}
                        )
                        response = await loop.run_in_executor(
                            None,
                            lambda: chat.send_message(
                                contents=genai_types.Content(
                                    role='tool',
                                    parts=[function_response_part]
                                )
                            )
                        )
                        return response.text
                    except Exception as skill_err:
                        logger.error(f"Skill execution error ({call.name}): {skill_err}")
                        return f"I tried to use a tool to help, but it failed: {str(skill_err)}"
            
            return response.text
        except Exception as e:
            logger.error(f"Error in generate_smart_answer: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                return "Gemini API Quota Exceeded. Please try again in a moment."
            return f"An error occurred while generating a smart answer: {str(e)}"
    
    async def translate_to_urdu(
        self,
        text: str
    ) -> str:
        """
        Translates text to Urdu using Gemini.
        Preserves markdown formatting, code blocks, and citations.
        """
        prompt = f"""You are a professional Urdu translator specializing in technical literature and robotics.

TASK:
Translate the following English text from a "Physical AI & Humanoid Robotics" book into Urdu.

RULES:
1. **Preserve Markdown**: Keep all headers (#), bold (**), italics (*), and lists format exactly as in the original.
2. **Code Blocks**: Do NOT translate content within code blocks or single backticks (`). Keep the code as is.
3. **Citations**: Do NOT translate citation patterns like [module:chapter:chunk_id].
4. **Natural Flow**: Use formal and technically accurate Urdu.
5. **Output**: Return ONLY the translated Urdu text.

TEXT TO TRANSLATE:
{text}

URDU TRANSLATION:"""

        # Generate response
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
        )
        
        return response.text.strip()
    
    def _extract_citations(
        self,
        answer_text: str,
        chunks: List[Dict[str, Any]]
    ) -> List[Citation]:
        """
        Extract citation references from the answer text.
        
        Matches [module:chapter:chunk_id] patterns and resolves to Citation objects.
        """
        citations = []
        seen_ids = set()
        
        # Pattern: [module-N:Chapter Title:chunk_id]
        pattern = r'\[([^:]+):([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, answer_text)
        
        for module, chapter, chunk_id in matches:
            # Skip duplicates
            if chunk_id in seen_ids:
                continue
            seen_ids.add(chunk_id)
            
            # Find matching chunk for URL
            source_url = ""
            score = None
            for chunk in chunks:
                if chunk.get("chunk_id") == chunk_id:
                    source_url = chunk.get("source_url", "")
                    score = chunk.get("score")
                    break
            
            citations.append(Citation(
                module=module.strip(),
                chapter=chapter.strip(),
                chunk_id=chunk_id.strip(),
                source_url=source_url,
                score=score
            ))
        
        # If no explicit citations found but we have chunks, add them as implicit sources
        if not citations and chunks:
            for chunk in chunks[:3]:  # Top 3 sources
                citations.append(Citation(
                    module=chunk.get("module", "unknown"),
                    chapter=chunk.get("chapter", "unknown"),
                    chunk_id=chunk.get("chunk_id", "unknown"),
                    source_url=chunk.get("source_url", ""),
                    score=chunk.get("score")
                ))
        
        return citations


@lru_cache()
def get_gemini_agent() -> GeminiAgent:
    """Get cached Gemini agent instance."""
    return GeminiAgent()


# Convenience functions for dependency injection

async def generate_rag_answer(
    query: str,
    chunks: List[Dict[str, Any]],
    history: List[Dict[str, Any]] = [],
    user_profile: Optional[Dict[str, Any]] = None,
    gamification_status: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[Citation]]:
    """Generate RAG answer using the default agent with optional personalization."""
    agent = get_gemini_agent()
    return await agent.generate_rag_answer(query, chunks, history, user_profile, gamification_status)


async def generate_selective_answer(query: str, selection_text: str) -> str:
    """Generate selective answer using the default agent."""
    agent = get_gemini_agent()
    return await agent.generate_selective_answer(query, selection_text)
