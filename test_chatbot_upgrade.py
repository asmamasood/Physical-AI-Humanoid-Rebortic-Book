"""
Test script for RAG Chatbot Upgrade

Tests all enhanced features:
1. Intent detection (SELECTED, SUMMARY, QUIZ, QA)
2. Context-aware greetings
3. System prompt improvements
4. Backward compatibility
"""

import asyncio
import sys
import io
from pathlib import Path

# Fix Windows console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.app.gemini_agent import GeminiAgent


class TestColors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print formatted test header"""
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'='*70}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}TEST: {test_name}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{'='*70}{TestColors.ENDC}\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = f"{TestColors.OKGREEN}✓ PASS{TestColors.ENDC}" if passed else f"{TestColors.FAIL}✗ FAIL{TestColors.ENDC}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {TestColors.OKCYAN}Details: {details}{TestColors.ENDC}")


def test_intent_detection():
    """Test enhanced intent detection"""
    print_test_header("Intent Detection Enhancement")

    agent = GeminiAgent()

    # Test cases: (query, selected_text, expected_intent)
    test_cases = [
        # SELECTED mode
        ("Explain this", "Some selected text here", "SELECTED"),
        ("What does this mean?", "Physical AI is...", "SELECTED"),

        # SUMMARY mode
        ("Summarize module 1", None, "SUMMARY"),
        ("Give me a brief overview", None, "SUMMARY"),
        ("What are the main points?", None, "SUMMARY"),
        ("Can you sum up chapter 2?", None, "SUMMARY"),
        ("tldr for module 3", None, "SUMMARY"),

        # QUIZ mode
        ("Create a quiz for chapter 1", None, "QUIZ"),
        ("Test me on robotics", None, "QUIZ"),
        ("Generate questions about AI", None, "QUIZ"),
        ("I want an assessment", None, "QUIZ"),
        ("Give me practice questions", None, "QUIZ"),

        # QA mode (explicit)
        ("What is Physical AI?", None, "QA"),
        ("Explain reinforcement learning", None, "QA"),
        ("Define humanoid robotics", None, "QA"),
        ("How does sensor fusion work?", None, "QA"),

        # QA mode (default)
        ("Tell me about robotics", None, "QA"),
        ("Robotics basics", None, "QA"),
    ]

    passed = 0
    failed = 0

    for query, selected_text, expected in test_cases:
        result = agent._detect_intent(query, selected_text)
        is_correct = result == expected

        if is_correct:
            passed += 1
        else:
            failed += 1

        status = "[PASS]" if is_correct else "[FAIL]"
        print(f"{status} Query: '{query}' | Expected: {expected} | Got: {result}")

    print(f"\n{TestColors.BOLD}Intent Detection Results:{TestColors.ENDC}")
    print(f"  {TestColors.OKGREEN}Passed: {passed}/{len(test_cases)}{TestColors.ENDC}")
    print(f"  {TestColors.FAIL}Failed: {failed}/{len(test_cases)}{TestColors.ENDC}")

    accuracy = (passed / len(test_cases)) * 100
    print(f"  {TestColors.OKCYAN}Accuracy: {accuracy:.1f}%{TestColors.ENDC}")

    return accuracy >= 95  # Target: 95% accuracy


def test_greeting_logic():
    """Test context-aware greeting logic"""
    print_test_header("Context-Aware Greeting Logic")

    agent = GeminiAgent()

    # Test cases: (response_text, should_contain)
    test_cases = [
        # Summary responses
        ("🎯 Key Topics\n• Physical AI\n• Robotics", "📖"),
        ("Summary: This chapter covers...", "📖"),

        # Quiz responses
        ("**Question 1** (Multiple Choice)\nWhat is AI?", "🎯"),
        ("Let's test your knowledge with these questions", "🎯"),

        # Not found responses
        ("I couldn't find information about that topic", "😊"),
        ("Unable to locate content about this", "😊"),

        # Standard responses
        ("Physical AI combines robotics with artificial intelligence.", "😊"),
        ("The book explains that humanoid robots...", "😊"),

        # Already has greeting (should not duplicate)
        ("Hello! Physical AI is fascinating.", None),  # None = no new greeting
        ("Hi there! Let me explain...", None),
    ]

    passed = 0
    failed = 0

    for response_text, expected_emoji in test_cases:
        result = agent._add_greetings(response_text)

        # Check if greeting was added appropriately
        if expected_emoji is None:
            # Should not change (already has greeting)
            is_correct = result == response_text
            check = "No duplicate greeting"
        else:
            # Should contain the expected emoji
            is_correct = expected_emoji in result and result.startswith(("Hello", "Hi"))
            check = f"Contains '{expected_emoji}' and friendly greeting"

        if is_correct:
            passed += 1
        else:
            failed += 1

        status = "[PASS]" if is_correct else "[FAIL]"
        print(f"{status} {check}")
        if not is_correct:
            print(f"  Input: {response_text[:60]}...")
            print(f"  Output: {result[:60]}...")

    print(f"\n{TestColors.BOLD}Greeting Logic Results:{TestColors.ENDC}")
    print(f"  {TestColors.OKGREEN}Passed: {passed}/{len(test_cases)}{TestColors.ENDC}")
    print(f"  {TestColors.FAIL}Failed: {failed}/{len(test_cases)}{TestColors.ENDC}")

    return failed == 0


def test_system_prompts():
    """Test that system prompts are properly formatted"""
    print_test_header("System Prompt Structure")

    from backend.app.gemini_agent import (
        SYSTEM_PROMPT_RAG,
        SYSTEM_PROMPT_SUMMARY,
        SYSTEM_PROMPT_QUIZ,
        SYSTEM_PROMPT_SELECTIVE
    )

    tests = []

    # Test RAG prompt
    rag_checks = [
        ("Contains format placeholders", "{context}" in SYSTEM_PROMPT_RAG),
        ("Contains query placeholder", "{query}" in SYSTEM_PROMPT_RAG),
        ("Contains history placeholder", "{history}" in SYSTEM_PROMPT_RAG),
        ("Contains profile placeholder", "{profile}" in SYSTEM_PROMPT_RAG),
        ("Mentions citations", "citation" in SYSTEM_PROMPT_RAG.lower()),
        ("Has clear rules", "RULES" in SYSTEM_PROMPT_RAG or "rules" in SYSTEM_PROMPT_RAG.lower()),
    ]

    # Test SUMMARY prompt
    summary_checks = [
        ("Contains context placeholder", "{context}" in SYSTEM_PROMPT_SUMMARY),
        ("Contains query placeholder", "{query}" in SYSTEM_PROMPT_SUMMARY),
        ("Has structured format", "Key Topics" in SYSTEM_PROMPT_SUMMARY),
        ("Includes emojis", "📖" in SYSTEM_PROMPT_SUMMARY or "✨" in SYSTEM_PROMPT_SUMMARY),
        ("Has clear rules", "RULES" in SYSTEM_PROMPT_SUMMARY),
    ]

    # Test QUIZ prompt
    quiz_checks = [
        ("Contains context placeholder", "{context}" in SYSTEM_PROMPT_QUIZ),
        ("Contains query placeholder", "{query}" in SYSTEM_PROMPT_QUIZ),
        ("Has question format", "Question" in SYSTEM_PROMPT_QUIZ),
        ("Includes answer format", "Answer" in SYSTEM_PROMPT_QUIZ),
        ("Has clear rules", "RULES" in SYSTEM_PROMPT_QUIZ),
        ("Mentions variety", "variety" in SYSTEM_PROMPT_QUIZ.lower() or "Multiple Choice" in SYSTEM_PROMPT_QUIZ),
    ]

    # Test SELECTIVE prompt
    selective_checks = [
        ("Contains selection placeholder", "{selection_text}" in SYSTEM_PROMPT_SELECTIVE),
        ("Contains query placeholder", "{query}" in SYSTEM_PROMPT_SELECTIVE),
        ("Emphasizes strictness", "ONLY" in SYSTEM_PROMPT_SELECTIVE),
    ]

    all_checks = [
        ("RAG Prompt", rag_checks),
        ("SUMMARY Prompt", summary_checks),
        ("QUIZ Prompt", quiz_checks),
        ("SELECTIVE Prompt", selective_checks),
    ]

    passed = 0
    failed = 0

    for prompt_name, checks in all_checks:
        print(f"\n{TestColors.BOLD}{prompt_name}:{TestColors.ENDC}")
        for check_name, result in checks:
            if result:
                passed += 1
                print(f"  {TestColors.OKGREEN}[OK]{TestColors.ENDC} {check_name}")
            else:
                failed += 1
                print(f"  {TestColors.FAIL}[NO]{TestColors.ENDC} {check_name}")

    total = passed + failed
    print(f"\n{TestColors.BOLD}System Prompt Results:{TestColors.ENDC}")
    print(f"  {TestColors.OKGREEN}Passed: {passed}/{total}{TestColors.ENDC}")
    print(f"  {TestColors.FAIL}Failed: {failed}/{total}{TestColors.ENDC}")

    return failed == 0


def test_backward_compatibility():
    """Test that existing functionality still works"""
    print_test_header("Backward Compatibility")

    agent = GeminiAgent()

    checks = [
        ("Agent instantiation", True),
        ("_detect_intent method exists", hasattr(agent, '_detect_intent')),
        ("_add_greetings method exists", hasattr(agent, '_add_greetings')),
        ("_format_profile method exists", hasattr(agent, '_format_profile')),
        ("_format_gamification method exists", hasattr(agent, '_format_gamification')),
        ("generate_rag_answer method exists", hasattr(agent, 'generate_rag_answer')),
        ("generate_selective_answer method exists", hasattr(agent, 'generate_selective_answer')),
        ("_extract_citations method exists", hasattr(agent, '_extract_citations')),
    ]

    passed = sum(1 for _, result in checks if result)
    failed = len(checks) - passed

    for check_name, result in checks:
        status = f"{TestColors.OKGREEN}[OK]{TestColors.ENDC}" if result else f"{TestColors.FAIL}[NO]{TestColors.ENDC}"
        print(f"  {status} {check_name}")

    print(f"\n{TestColors.BOLD}Compatibility Results:{TestColors.ENDC}")
    print(f"  {TestColors.OKGREEN}Passed: {passed}/{len(checks)}{TestColors.ENDC}")
    print(f"  {TestColors.FAIL}Failed: {failed}/{len(checks)}{TestColors.ENDC}")

    return failed == 0


def main():
    """Run all tests"""
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}")
    print("="*70)
    print("       RAG CHATBOT UPGRADE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"{TestColors.ENDC}\n")

    results = {}

    try:
        # Run all tests
        results['Intent Detection'] = test_intent_detection()
        results['Greeting Logic'] = test_greeting_logic()
        results['System Prompts'] = test_system_prompts()
        results['Backward Compatibility'] = test_backward_compatibility()

        # Summary
        print(f"\n{TestColors.HEADER}{TestColors.BOLD}")
        print("="*70)
        print("FINAL RESULTS")
        print("="*70)
        print(f"{TestColors.ENDC}")

        total_passed = sum(1 for passed in results.values() if passed)
        total_tests = len(results)

        for test_name, passed in results.items():
            status = f"{TestColors.OKGREEN}PASS{TestColors.ENDC}" if passed else f"{TestColors.FAIL}FAIL{TestColors.ENDC}"
            print(f"[{status}] {test_name}")

        print(f"\n{TestColors.BOLD}Overall:{TestColors.ENDC}")
        print(f"  {TestColors.OKGREEN}Passed: {total_passed}/{total_tests}{TestColors.ENDC}")
        print(f"  {TestColors.FAIL}Failed: {total_tests - total_passed}/{total_tests}{TestColors.ENDC}")

        if total_passed == total_tests:
            print(f"\n{TestColors.OKGREEN}{TestColors.BOLD}ALL TESTS PASSED! UPGRADE SUCCESSFUL!{TestColors.ENDC}\n")
            return 0
        else:
            print(f"\n{TestColors.WARNING}{TestColors.BOLD}SOME TESTS FAILED. REVIEW REQUIRED.{TestColors.ENDC}\n")
            return 1

    except Exception as e:
        print(f"\n{TestColors.FAIL}{TestColors.BOLD}ERROR: {e}{TestColors.ENDC}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
