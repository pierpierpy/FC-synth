"""
Validator for the FC dataset.
Checks whether the requested parameters are respected in the generated conversations.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    PASS = "✅"
    FAIL = "❌"
    WARN = "⚠️"
    SKIP = "⏭️"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    param_name: str
    expected: any
    observed: any
    status: ValidationStatus
    message: str
    
    def to_dict(self) -> Dict:
        return {
            "param": self.param_name,
            "expected": str(self.expected),
            "observed": str(self.observed),
            "status": self.status.value,
            "message": self.message
        }


@dataclass
class ExampleValidation:
    """Full validation of a single example."""
    example_id: str
    results: List[ValidationResult]

    @property
    def score(self) -> float:
        """Percentage of passed validations."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        total = sum(1 for r in self.results if r.status != ValidationStatus.SKIP)
        return passed / total if total > 0 else 0.0
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == ValidationStatus.PASS)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
    
    @property
    def warnings(self) -> int:
        return sum(1 for r in self.results if r.status == ValidationStatus.WARN)
    
    def to_dict(self) -> Dict:
        return {
            "example_id": self.example_id,
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "results": [r.to_dict() for r in self.results]
        }


# =============================================================================
# INDIVIDUAL VALIDATORS
# =============================================================================

def validate_call_type(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """Validate whether the call_type is respected (tool calls present or not)."""
    expected_type = params.get('call_type')
    num_calls = observed.get('num_tool_calls', 0)

    if expected_type == 'positive':
        if num_calls > 0:
            return ValidationResult(
                param_name="call_type",
                expected=f"positive (>0 tool calls)",
                observed=f"{num_calls} tool calls",
                status=ValidationStatus.PASS,
                message="Tool calls present as required"
            )
        else:
            return ValidationResult(
                param_name="call_type",
                expected=f"positive (>0 tool calls)",
                observed=f"0 tool calls",
                status=ValidationStatus.WARN,
                message="No tool call in a positive conversation"
            )

    elif expected_type == 'negative':
        if num_calls == 0:
            return ValidationResult(
                param_name="call_type",
                expected=f"negative (0 tool calls)",
                observed=f"0 tool calls",
                status=ValidationStatus.PASS,
                message="No tool call as required"
            )
        else:
            return ValidationResult(
                param_name="call_type",
                expected=f"negative (0 tool calls)",
                observed=f"{num_calls} tool calls",
                status=ValidationStatus.WARN,
                message="Tool calls present in a negative conversation"
            )

    elif expected_type == 'clarification':
        outcome = params.get('clarification_outcome')
        if outcome == 'resolved':
            if num_calls > 0:
                return ValidationResult(
                    param_name="call_type",
                    expected=f"clarification/resolved (>0 tool calls)",
                    observed=f"{num_calls} tool calls",
                    status=ValidationStatus.PASS,
                    message="Tool call after clarification as required"
                )
            else:
                return ValidationResult(
                    param_name="call_type",
                    expected=f"clarification/resolved (>0 tool calls)",
                    observed=f"0 tool calls",
                    status=ValidationStatus.WARN,
                    message="No tool call in clarification/resolved"
                )
        else:  # unresolved or partial
            if num_calls == 0:
                return ValidationResult(
                    param_name="call_type",
                    expected=f"clarification/{outcome} (0 tool calls)",
                    observed=f"0 tool calls",
                    status=ValidationStatus.PASS,
                    message="No tool call as required for an unresolved clarification"
                )
            else:
                return ValidationResult(
                    param_name="call_type",
                    expected=f"clarification/{outcome} (0 tool calls)",
                    observed=f"{num_calls} tool calls",
                    status=ValidationStatus.WARN,
                    message="Tool calls present in an unresolved clarification"
                )

    return ValidationResult(
        param_name="call_type",
        expected=expected_type,
        observed="unknown",
        status=ValidationStatus.SKIP,
        message="Unknown type"
    )


def validate_num_tool_calls(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """Validate the number of tool calls."""
    expected = params.get('num_tool_calls', 0)
    actual = observed.get('num_tool_calls', 0)

    # If expected is 0, it must be 0
    if expected == 0:
        if actual == 0:
            return ValidationResult(
                param_name="num_tool_calls",
                expected=0,
                observed=actual,
                status=ValidationStatus.PASS,
                message="No tool call as required"
            )
        else:
            return ValidationResult(
                param_name="num_tool_calls",
                expected=0,
                observed=actual,
                status=ValidationStatus.WARN,
                message=f"{actual} tool calls instead of 0"
            )

    # Tolerance: ±1 for num_tool_calls > 1
    if expected == actual:
        return ValidationResult(
            param_name="num_tool_calls",
            expected=expected,
            observed=actual,
            status=ValidationStatus.PASS,
            message="Exact number of tool calls"
        )
    elif abs(expected - actual) == 1 and expected > 1:
        return ValidationResult(
            param_name="num_tool_calls",
            expected=expected,
            observed=actual,
            status=ValidationStatus.WARN,
            message=f"Almost correct: {actual} instead of {expected}"
        )
    else:
        return ValidationResult(
            param_name="num_tool_calls",
            expected=expected,
            observed=actual,
            status=ValidationStatus.WARN,
            message=f"{actual} instead of {expected}"
        )


def validate_conversation_length(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """Validate the conversation length (loose check)."""
    expected_cat = params.get('conversation_length', 'medium')
    num_messages = observed.get('num_messages', 0)

    # Ranges per category (with overlap for flexibility)
    ranges = {
        'short': (2, 6),
        'medium': (4, 14),
        'long': (8, 22),
        'very_long': (15, 100)
    }

    min_msg, max_msg = ranges.get(expected_cat, (0, 100))

    # Extended tolerance: ±4 messages from the edges
    if min_msg <= num_messages <= max_msg:
        return ValidationResult(
            param_name="conversation_length",
            expected=f"{expected_cat} ({min_msg}-{max_msg})",
            observed=f"{num_messages} messages",
            status=ValidationStatus.PASS,
            message="Length correct"
        )
    elif num_messages >= (min_msg - 4) and num_messages <= (max_msg + 4):
        # Almost within range - always WARN, never FAIL
        return ValidationResult(
            param_name="conversation_length",
            expected=f"{expected_cat} ({min_msg}-{max_msg})",
            observed=f"{num_messages} messages",
            status=ValidationStatus.WARN,
            message=f"Acceptable length (tolerance ±4)"
        )
    else:
        # Far out of range - still only WARN
        return ValidationResult(
            param_name="conversation_length",
            expected=f"{expected_cat} ({min_msg}-{max_msg})",
            observed=f"{num_messages} messages",
            status=ValidationStatus.WARN,
            message=f"Length outside the ideal range"
        )


def validate_system_prompt_type(params: Dict, observed: Dict, messages: List[Dict], system_prompt: str) -> ValidationResult:
    """Validate the system prompt type."""
    expected = params.get('system_prompt_type', 'standard')

    if expected == 'none':
        if not system_prompt or system_prompt.strip() == "":
            return ValidationResult(
                param_name="system_prompt_type",
                expected="none",
                observed="absent",
                status=ValidationStatus.PASS,
                message="No system prompt as required"
            )
        else:
            return ValidationResult(
                param_name="system_prompt_type",
                expected="none",
                observed=f"{len(system_prompt.split())} words",
                status=ValidationStatus.WARN,
                message="System prompt present when not required"
            )

    # A system prompt should exist
    if not system_prompt or system_prompt.strip() == "":
        return ValidationResult(
            param_name="system_prompt_type",
            expected=expected,
            observed="absent",
            status=ValidationStatus.WARN,
            message="System prompt missing"
        )

    words = len(system_prompt.split())
    detected = observed.get('system_prompt_type', 'unknown')

    # Expected length mapping
    expected_ranges = {
        'minimal': (1, 20),
        'standard': (15, 80),
        'detailed': (50, 500)
    }
    
    min_w, max_w = expected_ranges.get(expected, (0, 500))
    
    if min_w <= words <= max_w:
        return ValidationResult(
            param_name="system_prompt_type",
            expected=f"{expected} ({min_w}-{max_w} words)",
            observed=f"{words} words",
            status=ValidationStatus.PASS,
            message="System prompt of the correct length"
        )
    else:
        # Wider tolerance
        if words < min_w:
            return ValidationResult(
                param_name="system_prompt_type",
                expected=f"{expected} ({min_w}-{max_w} words)",
                observed=f"{words} words",
                status=ValidationStatus.WARN,
                message="System prompt shorter than expected"
            )
        else:
            return ValidationResult(
                param_name="system_prompt_type",
                expected=f"{expected} ({min_w}-{max_w} words)",
                observed=f"{words} words",
                status=ValidationStatus.WARN,
                message="System prompt longer than expected"
            )


def validate_conversation_language(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """Validate the conversation language (USER messages only)."""
    expected = params.get('conversation_language', 'it')

    # Extract only the content of USER messages (ignore assistant and tool)
    user_texts = []
    for m in messages:
        if m.get('role') == 'user' and m.get('content'):
            user_texts.append(m['content'])

    combined_text = ' '.join(user_texts).lower()

    # Italian-language markers
    italian_markers = ['ciao', 'buongiorno', 'grazie', 'prego', 'vorrei', 'potrei',
                       'per favore', 'gentilmente', 'aiuto', 'problema', 'cosa', 'come',
                       'quando', 'dove', 'perché', 'quale', 'quanto', 'sono', 'ho', 'hai',
                       'è', 'siamo', 'volete', 'posso', 'puoi', 'deve', 'devo', 'salve',
                       'scusa', 'scusami', 'perfetto', 'ok', 'allora', 'quindi', 'però']
    
    italian_count = sum(1 for word in italian_markers if word in combined_text)
    detected = 'it' if italian_count >= 2 else 'en'
    
    if expected == detected:
        return ValidationResult(
            param_name="conversation_language",
            expected=expected,
            observed=f"{detected} ({italian_count} IT markers)",
            status=ValidationStatus.PASS,
            message=f"Correct language: {expected}"
        )
    elif italian_count >= 1 and expected == 'it':
        # At least a few Italian markers found
        return ValidationResult(
            param_name="conversation_language",
            expected=expected,
            observed=f"{detected} ({italian_count} IT markers)",
            status=ValidationStatus.WARN,
            message=f"Language probably correct (few markers)"
        )
    else:
        return ValidationResult(
            param_name="conversation_language",
            expected=expected,
            observed=f"{detected} ({italian_count} IT markers)",
            status=ValidationStatus.WARN,
            message=f"Detected language: {detected} (heuristic check)"
        )


def validate_first_tool_position(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """Validate the position of the first tool call (loose check, tolerance ±3)."""
    expected = params.get('first_tool_position', 0)
    actual = observed.get('first_tool_position', 0)

    # If expected is 0, there should be no tool call
    if expected == 0:
        if actual == 0:
            return ValidationResult(
                param_name="first_tool_position",
                expected="no tool call",
                observed="no tool call",
                status=ValidationStatus.PASS,
                message="No tool call as required"
            )
        else:
            # Tool call present but not expected - WARN not FAIL
            return ValidationResult(
                param_name="first_tool_position",
                expected="no tool call",
                observed=f"position {actual}",
                status=ValidationStatus.WARN,
                message="Tool call present (not critical)"
            )

    # ±3 tolerance counts as PASS, beyond that as WARN
    if actual == 0:
        return ValidationResult(
            param_name="first_tool_position",
            expected=f"position ~{expected}",
            observed="no tool call",
            status=ValidationStatus.WARN,
            message="No tool call found"
        )

    diff = abs(expected - actual)
    if diff <= 3:
        # Within ±3 positions = PASS
        return ValidationResult(
            param_name="first_tool_position",
            expected=f"position ~{expected}",
            observed=f"position {actual}",
            status=ValidationStatus.PASS,
            message=f"Position OK (diff={diff}, tolerance ±3)"
        )
    elif diff <= 5:
        # Within ±5 = WARN
        return ValidationResult(
            param_name="first_tool_position",
            expected=f"position ~{expected}",
            observed=f"position {actual}",
            status=ValidationStatus.WARN,
            message=f"Acceptable position (diff={diff})"
        )
    else:
        # Far off = still WARN (not critical)
        return ValidationResult(
            param_name="first_tool_position",
            expected=f"position ~{expected}",
            observed=f"position {actual}",
            status=ValidationStatus.WARN,
            message=f"Position differs from target (diff={diff})"
        )


def validate_parallel_tool_calls(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """
    Validate that there are no parallel tool calls (multiple tool_calls in the same assistant message).
    The target chat template (e.g. many Qwen/Llama templates) does not support parallel calls.
    """
    parallel_positions = []
    max_calls_in_msg = 0

    for i, m in enumerate(messages):
        if m.get('role') == 'assistant' and m.get('tool_calls'):
            num_tc = len(m['tool_calls'])
            max_calls_in_msg = max(max_calls_in_msg, num_tc)
            if num_tc > 1:
                parallel_positions.append((i, num_tc))

    if not parallel_positions:
        return ValidationResult(
            param_name="parallel_tool_calls",
            expected="1 tool_call per message",
            observed="OK (no parallel)",
            status=ValidationStatus.PASS,
            message="No parallel tool call"
        )

    # Parallel calls found - FAIL because they are not supported by the target chat template
    total_parallel = len(parallel_positions)
    return ValidationResult(
        param_name="parallel_tool_calls",
        expected="1 tool_call per message",
        observed=f"{total_parallel} messages with parallel (max {max_calls_in_msg})",
        status=ValidationStatus.FAIL,
        message=f"ERROR: {total_parallel} messages have multiple tool_calls (not supported by the target chat template)"
    )


def validate_consecutive_roles(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """
    Validate that there are no PROBLEMATIC consecutive messages with the same role.

    WRONG (reflection before the tool):
        user -> assistant (content) -> assistant (tool_call)

    OK (comment after a tool + new action):
        tool -> assistant (content) -> assistant (tool_call)

    The difference: if a tool precedes the assistant-assistant pair, it is OK.
    """
    if len(messages) < 2:
        return ValidationResult(
            param_name="consecutive_roles",
            expected="no problematic consecutive roles",
            observed="conversation too short",
            status=ValidationStatus.SKIP,
            message="Conversation too short to validate"
        )

    problematic_consecutive = []

    for i in range(1, len(messages)):
        prev_role = messages[i-1].get('role')
        curr_role = messages[i].get('role')

        if prev_role == curr_role:
            # Consecutive tool-tool messages are always OK (parallel tools)
            if curr_role == 'tool':
                continue

            # Assistant-assistant: check if it follows a tool (OK) or a user (PROBLEM)
            if curr_role == 'assistant':
                # Look for the previous non-assistant message
                prev_non_assistant_role = None
                for j in range(i-2, -1, -1):
                    if messages[j].get('role') != 'assistant':
                        prev_non_assistant_role = messages[j].get('role')
                        break
                
                # If a tool came before -> OK (comment + new action)
                if prev_non_assistant_role == 'tool':
                    continue

                # If a user came before -> PROBLEM (pointless reflection)
                problematic_consecutive.append((i-1, i, 'assistant', prev_non_assistant_role))
            else:
                # Other consecutive roles (user-user)
                problematic_consecutive.append((i-1, i, curr_role, None))

    if not problematic_consecutive:
        return ValidationResult(
            param_name="consecutive_roles",
            expected="no problematic consecutive roles",
            observed="OK",
            status=ValidationStatus.PASS,
            message="Message structure correct"
        )

    # Check whether there are problematic assistant-assistant pairs (after a user)
    bad_assistant = [c for c in problematic_consecutive if c[2] == 'assistant']

    if bad_assistant:
        return ValidationResult(
            param_name="consecutive_roles",
            expected="no consecutive assistant messages after a user",
            observed=f"{len(bad_assistant)} pointless reflections",
            status=ValidationStatus.FAIL,
            message=f"ERROR: consecutive assistant messages (reflection before a tool)"
        )

    # Other consecutive roles (user-user) are warnings
    return ValidationResult(
        param_name="consecutive_roles",
        expected="no problematic consecutive roles",
        observed=f"{len(problematic_consecutive)} consecutive",
        status=ValidationStatus.WARN,
        message=f"Consecutive roles: {[c[2] for c in problematic_consecutive]}"
    )


def validate_out_of_scope_requests(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """
    Validate that the number of out-of-scope requests (which the assistant cannot handle
    with the tools) is at least the required amount.

    Patterns to recognize out-of-scope responses:
    - Italian: "non posso" / "non sono in grado"
    - Italian: "non ho accesso" / "non ho la possibilità"
    - Italian: "non dispongo di" / "non ho strumenti"
    - Italian: "non è possibile" / "impossibile per me"
    - English: "can't", "cannot", "don't have access", "not able to"
    """
    expected = params.get('out_of_scope_requests', 0)
    call_type = params.get('call_type', '')

    # If out_of_scope_requests = 0, it is valid by default
    if expected == 0:
        return ValidationResult(
            param_name="out_of_scope_requests",
            expected="0 (none)",
            observed="N/A",
            status=ValidationStatus.SKIP,
            message="No out-of-scope required"
        )

    # Only positive and clarification/resolved should have out_of_scope_requests > 0
    if not (call_type == 'positive' or call_type == 'clarification/resolved'):
        return ValidationResult(
            param_name="out_of_scope_requests",
            expected=str(expected),
            observed="N/A",
            status=ValidationStatus.SKIP,
            message=f"Out-of-scope not applicable to {call_type}"
        )

    # Patterns to identify "I can't" responses
    out_of_scope_patterns_it = [
        'non posso', 'non sono in grado', 'non ho accesso', 'non ho la possibilità',
        'non dispongo di', 'non ho strumenti', 'non è possibile per me',
        'al di fuori delle mie capacità', 'oltre le mie capacità',
        'non rientra nelle mie funzionalità', 'non ho le funzionalità',
        'non mi è possibile', 'mi risulta impossibile', 'non ho modo di',
        'non ho uno strumento', 'non ho un tool', 'non ho la funzione'
    ]
    out_of_scope_patterns_en = [
        "can't help", "cannot help", "can't assist", "cannot assist",
        "don't have access", "do not have access", "not able to",
        "unable to", "beyond my capabilities", "outside my capabilities",
        "don't have the ability", "do not have the ability",
        "not within my capabilities", "i'm not able to",
        # More generic patterns to catch "I can't X"
        "i can't", "i cannot", "i don't have", "i do not have",
        "no tool", "no function", "no capability"
    ]

    all_patterns = out_of_scope_patterns_it + out_of_scope_patterns_en

    # Count the assistant messages that contain out-of-scope patterns
    assistant_texts = [
        (m.get('content') or '').lower() 
        for m in messages 
        if m.get('role') == 'assistant' and m.get('content')
    ]
    
    out_of_scope_count = 0
    for text in assistant_texts:
        if any(pattern in text for pattern in all_patterns):
            out_of_scope_count += 1
    
    if out_of_scope_count >= expected:
        return ValidationResult(
            param_name="out_of_scope_requests",
            expected=str(expected),
            observed=str(out_of_scope_count),
            status=ValidationStatus.PASS,
            message=f"Found {out_of_scope_count} out-of-scope responses (required >={expected})"
        )
    else:
        return ValidationResult(
            param_name="out_of_scope_requests",
            expected=str(expected),
            observed=str(out_of_scope_count),
            status=ValidationStatus.WARN,  # WARN because it is heuristic
            message=f"Only {out_of_scope_count} out-of-scope responses (required {expected})"
        )


def validate_user_style(params: Dict, observed: Dict, messages: List[Dict]) -> ValidationResult:
    """
    Validate the user's style (heuristic analysis).
    This is an approximate validation based on linguistic patterns.
    """
    expected = params.get('user_style', 'informal')

    # Extract the text of the user messages
    user_texts = [m.get('content', '') or '' for m in messages if m.get('role') == 'user']
    combined_text = " ".join(user_texts).lower()

    if not combined_text:
        return ValidationResult(
            param_name="user_style",
            expected=expected,
            observed="no user messages",
            status=ValidationStatus.SKIP,
            message="No user message to analyze"
        )

    # Style markers
    formal_markers = ['gentilmente', 'cortesemente', 'le chiedo', 'vorrei', 'le sarei',
                      'la ringrazio', 'distinti saluti', 'buongiorno', 'avrei bisogno',
                      'would you', 'could you please', 'i would like', 'kindly']
    
    informal_markers = ['ciao', 'hey', 'ehi', 'ok', 'grazie mille', 'bene!', 'top',
                        'senti', 'fammi', 'dimmi', 'hi', 'thanks!', 'cool', 'yep']
    
    telegraphic_markers = len(combined_text.split()) / max(len(user_texts), 1)  # average words per msg

    frustrated_markers = ['!!!', 'assurdo', 'vergognoso', 'inaccettabile', 'ridicolo',
                          'impossibile', 'scandaloso', 'absurd', 'unacceptable', 'ridiculous']
    
    confused_markers = ['non capisco', 'non ho capito', 'cosa significa', 'mi spieghi',
                        "don't understand", 'confused', 'what does', 'can you explain']
    
    # Score for each style
    scores = {
        'formal': sum(1 for m in formal_markers if m in combined_text),
        'informal': sum(1 for m in informal_markers if m in combined_text),
        'telegraphic': 1 if telegraphic_markers < 6 else 0,  # fewer than 6 words per msg
        'frustrated': sum(1 for m in frustrated_markers if m in combined_text),
        'confused': sum(1 for m in confused_markers if m in combined_text),
        'vague': 1 if any(w in combined_text for w in ['quello', 'quella cosa', 'il coso', 'that thing']) else 0,
        'verbose': 1 if telegraphic_markers > 25 else 0  # more than 25 words per msg
    }

    # Find the dominant style
    detected_style = max(scores.keys(), key=lambda k: scores[k])
    max_score = scores[detected_style]

    if max_score == 0:
        detected_style = 'informal'  # default

    if expected == detected_style:
        return ValidationResult(
            param_name="user_style",
            expected=expected,
            observed=detected_style,
            status=ValidationStatus.PASS,
            message=f"User style correct"
        )
    elif scores.get(expected, 0) > 0:
        return ValidationResult(
            param_name="user_style",
            expected=expected,
            observed=f"{detected_style} (but {expected} present)",
            status=ValidationStatus.WARN,
            message=f"Style {expected} present but not dominant"
        )
    else:
        return ValidationResult(
            param_name="user_style",
            expected=expected,
            observed=detected_style,
            status=ValidationStatus.WARN,  # WARN instead of FAIL because it is heuristic
            message=f"Detected style: {detected_style}"
        )


# =============================================================================
# FULL VALIDATION
# =============================================================================

def validate_example(example_dict: Dict) -> ExampleValidation:
    """
    Validate a single example.

    Args:
        example_dict: dict with keys: id, params, observed, messages, system_prompt

    Returns:
        ExampleValidation with all the results
    """
    example_id = example_dict.get('id', 'unknown')
    params = example_dict.get('params', {})
    observed = example_dict.get('observed', {})
    messages = example_dict.get('messages', [])
    system_prompt = example_dict.get('system_prompt', '')
    
    results = []
    
    # 1. Call type
    results.append(validate_call_type(params, observed, messages))
    
    # 2. Num tool calls  
    results.append(validate_num_tool_calls(params, observed, messages))
    
    # 3. Conversation length
    results.append(validate_conversation_length(params, observed, messages))
    
    # 4. System prompt type
    results.append(validate_system_prompt_type(params, observed, messages, system_prompt))
    
    # 5. Conversation language
    results.append(validate_conversation_language(params, observed, messages))
    
    # 6. First tool position
    results.append(validate_first_tool_position(params, observed, messages))
    
    # 7. User style
    results.append(validate_user_style(params, observed, messages))
    
    # 8. Consecutive roles (no assistant-assistant)
    results.append(validate_consecutive_roles(params, observed, messages))
    
    # 9. Parallel tool calls (multiple tool_calls in same assistant message)
    results.append(validate_parallel_tool_calls(params, observed, messages))
    
    # 10. Out of scope requests
    results.append(validate_out_of_scope_requests(params, observed, messages))
    
    return ExampleValidation(example_id=example_id, results=results)


def validate_batch(examples: List[Dict]) -> Dict:
    """
    Validate a batch of examples.

    Args:
        examples: list of example dicts

    Returns:
        Dict with aggregate statistics and individual validations
    """
    validations = [validate_example(ex) for ex in examples]

    # Aggregate statistics
    total_pass = sum(v.passed for v in validations)
    total_fail = sum(v.failed for v in validations)
    total_warn = sum(v.warnings for v in validations)

    avg_score = sum(v.score for v in validations) / len(validations) if validations else 0

    # Per-parameter statistics
    param_stats = {}
    for v in validations:
        for r in v.results:
            if r.param_name not in param_stats:
                param_stats[r.param_name] = {'pass': 0, 'fail': 0, 'warn': 0, 'skip': 0}
            param_stats[r.param_name][r.status.name.lower()] += 1
    
    return {
        "summary": {
            "total_examples": len(examples),
            "average_score": round(avg_score * 100, 1),
            "total_pass": total_pass,
            "total_fail": total_fail,
            "total_warn": total_warn
        },
        "by_parameter": param_stats,
        "validations": [v.to_dict() for v in validations]
    }


def print_validation_summary(validation_result: Dict):
    """Print a summary of the validation."""
    summary = validation_result['summary']
    by_param = validation_result['by_parameter']
    
    print("\n" + "="*60)
    print("                  VALIDATION SUMMARY")
    print("="*60)
    print(f"Total examples: {summary['total_examples']}")
    print(f"Average score:  {summary['average_score']}%")
    print(f"Total: ✅ {summary['total_pass']} | ❌ {summary['total_fail']} | ⚠️ {summary['total_warn']}")
    
    print("\n" + "-"*60)
    print("BY PARAMETER:")
    print("-"*60)
    for param, stats in by_param.items():
        total = stats['pass'] + stats['fail'] + stats['warn']
        pct = (stats['pass'] / total * 100) if total > 0 else 0
        print(f"  {param:25} | ✅{stats['pass']:3} ❌{stats['fail']:3} ⚠️{stats['warn']:3} | {pct:5.1f}%")
    
    print("="*60)


if __name__ == "__main__":
    # Test with a dummy example
    test_example = {
        "id": "test123",
        "params": {
            "call_type": "positive",
            "positive_type": "direct",
            "num_tool_calls": 1,
            "conversation_length": "medium",
            "system_prompt_type": "standard",
            "conversation_language": "it",
            "first_tool_position": 2,
            "user_style": "informal"
        },
        "observed": {
            "num_tool_calls": 1,
            "num_messages": 6,
            "system_prompt_type": "standard",
            "conversation_language": "it",
            "first_tool_position": 2
        },
        "messages": [
            {"role": "user", "content": "Ciao, mi servirebbe una cosa"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "1"}]},
            {"role": "tool", "content": "..."},
            {"role": "assistant", "content": "Ecco fatto!"}
        ],
        "system_prompt": "Sei un assistente utile. Aiuti gli utenti con le loro richieste in modo cortese e professionale."
    }
    
    validation = validate_example(test_example)
    print(f"Score: {validation.score*100:.1f}%")
    for r in validation.results:
        print(f"  {r.status.value} {r.param_name}: {r.message}")
