"""
TarkAI — Curriculum Knowledge Base
Curated engineering tracks with tiered algorithmic challenges,
test case assertions, and Socratic guidance scaffolds.
"""

from typing import Dict, List, Optional
from models import ChallengeMetadata, TestCase


CHALLENGES: Dict[str, Dict] = {
    "two_sum_sorted": {
        "id": "two_sum_sorted",
        "title": "Two Pointer Target Sum",
        "track": "Track 1: Algorithmic Fundamentals",
        "difficulty": "Easy",
        "summary": "Find two numbers in a sorted array that sum to target in O(N) time and O(1) space.",
        "description": """### Problem Statement
Given a **1-indexed** array of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number.

Return the indices of the two numbers, `[index1, index2]`, as an integer array of length 2 where `1 <= index1 < index2 <= numbers.length`.

### Algorithmic Requirement
Your solution must use only **O(1) additional space** and run in **O(N) time**. Avoid nested loops ($O(N^2)$) or auxiliary hash maps ($O(N)$ space).""",
        "constraints": [
            "2 <= len(numbers) <= 3 * 10^4",
            "-1000 <= numbers[i] <= 1000",
            "numbers is sorted in non-decreasing order",
            "Time Complexity: O(N)",
            "Space Complexity: O(1)"
        ],
        "starter_code": """def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    \"\"\"
    Find two 1-indexed numbers that add up to target.
    Must run in O(N) time and O(1) space.
    \"\"\"
    # Hint: Use two pointers at the boundaries
    left = 0
    right = len(numbers) - 1
    
    # Write your solution here
    return []
""",
        "test_cases": [
            TestCase(description="Standard sorted pair", call="two_sum_sorted([2, 7, 11, 15], 9)", expected=[1, 2]),
            TestCase(description="Negative and positive integers", call="two_sum_sorted([-3, 3, 4, 90], 0)", expected=[1, 2]),
            TestCase(description="Duplicate values summing to target", call="two_sum_sorted([2, 3, 4, 4], 8)", expected=[3, 4]),
            TestCase(description="Endpoints summing to target", call="two_sum_sorted([1, 2, 3, 4, 10], 11)", expected=[1, 5]),
            TestCase(description="Adjacent pair at array end", call="two_sum_sorted([0, 0, 3, 4], 0)", expected=[1, 2])
        ],
        "hints": {
            1: {
                "title": "Invariant of Sorted Order",
                "guidance": "Since the array is already sorted, notice what happens if you test the extreme elements (the smallest at index 0, and largest at index n-1). If their sum is greater than your target, which pointer is the only one that could possibly decrease the sum?",
                "question": "Can moving the left pointer ever help you when the current sum is already too large?"
            },
            2: {
                "title": "Two-Pointer Convergence",
                "guidance": "Initialize two pointers: `left = 0` and `right = len(numbers) - 1`. Calculate `current_sum = numbers[left] + numbers[right]`. If `current_sum > target`, decrement `right`. If `current_sum < target`, increment `left`.",
                "question": "Remember that indices are 1-based in the output. Did you add 1 to your 0-based indices?"
            },
            3: {
                "title": "Algorithmic Scaffold",
                "guidance": """while left < right:
    s = numbers[left] + numbers[right]
    if s == target:
        return [left + 1, right + 1]
    elif s < target:
        left += 1
    else:
        right -= 1""",
                "question": "Does your loop terminate safely if no valid pair exists?"
            }
        }
    },

    "longest_unique_substring": {
        "id": "longest_unique_substring",
        "title": "Sliding Window Unique Substring",
        "track": "Track 1: Algorithmic Fundamentals",
        "difficulty": "Medium",
        "summary": "Calculate length of longest substring without repeating characters in O(N) time.",
        "description": """### Problem Statement
Given a string `s`, find the length of the **longest substring** without duplicate characters.

### Examples
- `"abcabcbb"` -> `3` (the substring `"abc"`)
- `"bbbbb"` -> `1` (the substring `"b"`)
- `"pwwkew"` -> `3` (the substring `"wke"`)

### Constraints
- Running in $O(N)$ with a dynamic sliding window. Avoid generating all $O(N^2)$ substrings.""",
        "constraints": [
            "0 <= len(s) <= 5 * 10^4",
            "s consists of English letters, digits, symbols and spaces.",
            "Target Time Complexity: O(N)",
            "Target Space Complexity: O(min(M, N)) where M is alphabet size"
        ],
        "starter_code": """def length_of_longest_substring(s: str) -> int:
    \"\"\"
    Compute length of longest substring without duplicate characters.
    Time complexity must be O(N).
    \"\"\"
    # Maintain a sliding window [start...end]
    seen = {}
    max_len = 0
    start = 0
    
    # Write your solution here
    return max_len
""",
        "test_cases": [
            TestCase(description="Multi-character repeats", call="length_of_longest_substring('abcabcbb')", expected=3),
            TestCase(description="Identical character sequence", call="length_of_longest_substring('bbbbb')", expected=1),
            TestCase(description="Overlapping internal substring", call="length_of_longest_substring('pwwkew')", expected=3),
            TestCase(description="Empty string boundary", call="length_of_longest_substring('')", expected=0),
            TestCase(description="Whitespace and punctuation", call="length_of_longest_substring('tark ai 2026')", expected=9)
        ],
        "hints": {
            1: {
                "title": "Window Invariant",
                "guidance": "Think of the substring as a window `[start, end]`. When you encounter a character already in your window, what is the new valid `start` position?",
                "question": "Can you jump the `start` pointer directly to one position past the previous occurrence of the duplicate character?"
            },
            2: {
                "title": "Hash Map Memory",
                "guidance": "Keep a dictionary mapping each character to its most recent index: `seen[char] = end`. When `char in seen and seen[char] >= start`, update `start = seen[char] + 1`.",
                "question": "Why is the check `seen[char] >= start` necessary when examining previously recorded indices?"
            },
            3: {
                "title": "Window Expansion",
                "guidance": """for end, char in enumerate(s):
    if char in seen and seen[char] >= start:
        start = seen[char] + 1
    seen[char] = end
    max_len = max(max_len, end - start + 1)
return max_len""",
                "question": "How does updating `max_len` at every step guarantee capturing the global optimum?"
            }
        }
    },

    "max_subarray_kadane": {
        "id": "max_subarray_kadane",
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "track": "Track 2: Dynamic Programming & Invariants",
        "difficulty": "Medium",
        "summary": "Find contiguous subarray with largest sum in single pass O(N) time and O(1) space.",
        "description": """### Problem Statement
Given an integer array `nums`, find the subarray with the largest sum, and return its sum.

A **subarray** is a contiguous non-empty sequence of elements within an array.

### Engineering Challenge
A naive double loop checks all pairs in $O(N^2)$. Your task is to implement **Kadane's Algorithm** to solve this in **O(N) time and O(1) space** with a single traversal.""",
        "constraints": [
            "1 <= len(nums) <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
            "Time Complexity: O(N)",
            "Space Complexity: O(1)"
        ],
        "starter_code": """def max_sub_array(nums: list[int]) -> int:
    \"\"\"
    Calculate max contiguous subarray sum in O(N) time and O(1) space.
    \"\"\"
    if not nums:
        return 0
        
    current_max = nums[0]
    global_max = nums[0]
    
    # Implement Kadane's single-pass loop
    return global_max
""",
        "test_cases": [
            TestCase(description="Mixed positive and negative values", call="max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4])", expected=6),
            TestCase(description="Single element array", call="max_sub_array([1])", expected=1),
            TestCase(description="All negative array", call="max_sub_array([-5, -2, -8, -1, -4])", expected=-1),
            TestCase(description="All positive values", call="max_sub_array([5, 4, -1, 7, 8])", expected=23),
            TestCase(description="Zero crossing array", call="max_sub_array([-1, 0, -2])", expected=0)
        ],
        "hints": {
            1: {
                "title": "Local vs Global Decision",
                "guidance": "At each step `i`, you must make a choice: either append `nums[i]` to the existing running subarray, or abandon the previous subarray and start a fresh subarray at `nums[i]`. When is it better to abandon?",
                "question": "If your previous running sum became negative, will adding it to `nums[i]` ever help you produce a larger total than starting fresh?"
            },
            2: {
                "title": "Kadane Invariant",
                "guidance": "The recurrence relation is: `current_max = max(nums[i], current_max + nums[i])`. Then update `global_max = max(global_max, current_max)`.",
                "question": "Why must `global_max` be initialized to `nums[0]` rather than `0` to handle arrays with only negative numbers?"
            },
            3: {
                "title": "Loop Implementation",
                "guidance": """for num in nums[1:]:
    current_max = max(num, current_max + num)
    if current_max > global_max:
        global_max = current_max
return global_max""",
                "question": "What is the memory footprint of this single-pass state machine?"
            }
        }
    },

    "streaming_batch_generator": {
        "id": "streaming_batch_generator",
        "title": "Streaming Memory-Efficient Batch Generator",
        "track": "Track 3: Production Python Systems",
        "difficulty": "Medium",
        "summary": "Build a generator yielding fixed-size batches from large iterables with zero memory bloat.",
        "description": """### Problem Statement
In production data pipelines (e.g. streaming LLM tokens or database bulk inserts), loading a 10M-item dataset into a list causes memory exhaustion ($O(N)$ RAM spike).

Write a generator function `batch_stream(iterable, batch_size)` that yields lists of at most `batch_size` items sequentially.

### Requirements
- Must be an authentic Python generator yielding batches lazily (`yield`).
- Must handle iterators/generators whose length is not known in advance (do not call `len()` or slice `[:]`).
- The final batch may contain fewer than `batch_size` items if the input is exhausted.""",
        "constraints": [
            "batch_size >= 1",
            "Memory complexity must be O(batch_size), not O(N)",
            "Do not consume the entire iterable upfront"
        ],
        "starter_code": """from typing import Iterable, Any, Generator, List

def batch_stream(iterable: Iterable[Any], batch_size: int) -> Generator[List[Any], None, None]:
    \"\"\"
    Yield successive batches of size `batch_size` from iterable lazily.
    Must maintain O(batch_size) memory complexity.
    \"\"\"
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
            
    if batch:
        yield batch
""",
        "test_cases": [
            TestCase(description="Exact multiple batching", call="list(batch_stream([1, 2, 3, 4], 2))", expected=[[1, 2], [3, 4]]),
            TestCase(description="Remainder final batch", call="list(batch_stream(range(5), 2))", expected=[[0, 1], [2, 3], [4]]),
            TestCase(description="Single batch larger than data", call="list(batch_stream(['a', 'b'], 10))", expected=[['a', 'b']]),
            TestCase(description="Batch size of 1", call="list(batch_stream([10, 20], 1))", expected=[[10], [20]]),
            TestCase(description="Empty iterable generator", call="list(batch_stream([], 3))", expected=[])
        ],
        "hints": {
            1: {
                "title": "Lazy Iteration",
                "guidance": "Using `yield` inside a loop transforms your function into a generator iterator. Make sure you don't convert the input iterable into a list with `list(iterable)` at the start, as that defeats the memory-saving goal.",
                "question": "What happens if the input is an infinite generator or stream?"
            },
            2: {
                "title": "Buffer Cleanup",
                "guidance": "After yielding `batch`, remember to reset it to a new empty list `[]` rather than mutating or retaining references in memory.",
                "question": "Did you handle the remainder elements left in the buffer when the iterator finishes?"
            },
            3: {
                "title": "Alternative with itertools",
                "guidance": "You can also use `itertools.islice` over the iterator: `it = iter(iterable); chunk = list(islice(it, batch_size))` in a while loop until chunk is empty.",
                "question": "Which approach is more readable for your team?"
            }
        }
    },

    "valid_parentheses_stack": {
        "id": "valid_parentheses_stack",
        "title": "Syntax Bracket Validator (Stack Invariant)",
        "track": "Track 2: Dynamic Programming & Invariants",
        "difficulty": "Easy",
        "summary": "Verify matching brackets string using LIFO stack invariant in O(N) time.",
        "description": """### Problem Statement
Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

### Complexity Requirement
- Time Complexity: $O(N)$
- Space Complexity: $O(N)$ using a LIFO Stack.""",
        "constraints": [
            "1 <= len(s) <= 10^4",
            "s consists of parentheses only '()[]{}'.",
            "Time: O(N), Space: O(N)"
        ],
        "starter_code": """def is_valid_parentheses(s: str) -> bool:
    \"\"\"
    Return True if bracket sequence is structurally valid, False otherwise.
    \"\"\"
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    # Write your stack solution here
    return len(stack) == 0
""",
        "test_cases": [
            TestCase(description="Simple round brackets", call="is_valid_parentheses('()')", expected=True),
            TestCase(description="Multiple bracket types", call="is_valid_parentheses('()[]{}')", expected=True),
            TestCase(description="Mismatched pair", call="is_valid_parentheses('(]')", expected=False),
            TestCase(description="Nested valid brackets", call="is_valid_parentheses('([{}])')", expected=True),
            TestCase(description="Unclosed opening bracket", call="is_valid_parentheses('((')", expected=False),
            TestCase(description="Dangling closing bracket", call="is_valid_parentheses(']')", expected=False)
        ],
        "hints": {
            1: {
                "title": "LIFO Semantics",
                "guidance": "Parentheses follow a Last-In, First-Out (LIFO) pattern. The most recently opened bracket must be the first one closed.",
                "question": "What data structure in Python natively supports O(1) push and pop operations?"
            },
            2: {
                "title": "Lookup Map",
                "guidance": "Use a map of closing bracket to opening bracket: `mapping = {')': '(', '}': '{', ']': '['}`. When you see a closing bracket, pop the top of your stack and assert they match.",
                "question": "What should happen if you see a closing bracket when your stack is empty?"
            },
            3: {
                "title": "Stack Loop",
                "guidance": """for char in s:
    if char in mapping:
        top_element = stack.pop() if stack else '#'
        if mapping[char] != top_element:
            return False
    else:
        stack.append(char)
return not stack""",
                "question": "Why is `return not stack` essential at the end?"
            }
        }
    }
}


def get_all_challenges() -> List[ChallengeMetadata]:
    """Returns metadata for all curriculum challenges."""
    results = []
    for c in CHALLENGES.values():
        results.append(ChallengeMetadata(
            id=c["id"],
            title=c["title"],
            track=c["track"],
            difficulty=c["difficulty"],
            summary=c["summary"],
            description=c["description"],
            constraints=c["constraints"],
            starter_code=c["starter_code"],
            test_count=len(c["test_cases"]),
            solved=False
        ))
    return results


def get_challenge_by_id(challenge_id: str) -> Optional[Dict]:
    """Retrieves full challenge specification by ID."""
    return CHALLENGES.get(challenge_id)
