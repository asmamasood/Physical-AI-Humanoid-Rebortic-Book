"""
Modular Skill Registry for Gemini Tool-Calling.

Provides a central location to register and retrieve Python functions
that can be used as tools by the Agent Orchestrator.
"""

import inspect
from typing import Dict, Any, Callable, List, Optional
from google.genai import types as genai_types


class SkillRegistry:
    """Registry for AI Skills/Subagents."""
    
    def __init__(self):
        self._skills: Dict[str, Callable] = {}
        self._tool_definitions: List[genai_types.FunctionDeclaration] = []

    def register(self, name: Optional[str] = None):
        """
        Decorator to register a function as a skill.
        
        Extracts documentation and parameter info for Gemini.
        """
        def decorator(func: Callable):
            skill_name = name or func.__name__
            self._skills[skill_name] = func
            
            # Extract parameters for Gemini
            sig = inspect.signature(func)
            doc = func.__doc__ or "No description provided."
            
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param_name == "user_id": 
                    continue
                    
                # Map Python types to JSON Schema types
                p_type = "string"
                if param.annotation == int:
                    p_type = "integer"
                elif param.annotation == float:
                    p_type = "number"
                elif param.annotation == bool:
                    p_type = "boolean"
                
                properties[param_name] = {
                    "type": p_type,
                    "description": f"Parameter {param_name}"
                }
                
                if param.default is inspect.Parameter.empty:
                    required.append(param_name)
            
            # New SDK: Use FunctionDeclaration with JSON schema
            declaration = genai_types.FunctionDeclaration(
                name=skill_name,
                description=doc.strip().split('\n')[0],  # Use first line as short desc
                parameters_json_schema={
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            )
            
            self._tool_definitions.append(declaration)
            
            return func
        return decorator

    def get_skill(self, name: str) -> Optional[Callable]:
        """Retrieve a skill by name."""
        return self._skills.get(name)

    def get_all_tool_definitions(self) -> List[genai_types.Tool]:
        """Return definitions for Gemini's tool config."""
        if not self._tool_definitions:
            return []
        return [genai_types.Tool(function_declarations=self._tool_definitions)]


# Global registry instance
registry = SkillRegistry()
