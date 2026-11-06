"""
TarkAI (तर्क) — Master Curriculum Knowledge Base
Comprehensive 4-track curriculum with 10 production-grade engineering challenges,
edge-case test assertions, and multi-tier Socratic pedagogical guidance.
"""

from typing import Dict, List, Optional
from models import ChallengeMetadata, TestCase


CHALLENGES: Dict[str, Dict] = {
    # -------------------------------------------------------------------------
    # TRACK 1: High-Performance Algorithmic Invariants
    # -------------------------------------------------------------------------
    "two_sum_sorted": {
        "id": "two_sum_sorted",
        "title": "Two-Pointer Target Sum",
        "track": "Track 1: Algorithmic Invariants",
        "track_code": "ALG-101",
        "difficulty": "Easy",
        "summary": "Find two numbers in a sorted array that sum to target in O(N) time and O(1) space.",
        "description": r"""### Problem Statement
Given a **1-indexed** array of integers `numbers` sorted in non-decreasing order, return the 1-based indices `[index1, index2]` of two numbers that add up to `target`.

### Engineering Invariant
A naive double loop executes in $O(N^2)$. Using a hash map achieves $O(N)$ time but wastes $O(N)$ auxiliary memory. Your task is to exploit the sorted invariant using **two pointers converging from boundaries** in **O(N) time and O(1) space**.""",
        "constraints": [
            "2 <= len(numbers) <= 3 * 10^4",
            "-1000 <= numbers[i] <= 1000",
            "Sorted in non-decreasing order",
            "Target Time Complexity: O(N)",
            "Target Space Complexity: O(1)"
        ],
        "starter_code": """def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    \"\"\"
    Find two 1-indexed numbers that add up to target.
    Must run in O(N) time and O(1) space.
    \"\"\"
    left = 0
    right = len(numbers) - 1
    
    # Converge pointers based on sum
    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return [left + 1, right + 1]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
            
    return []
""",
        "test_cases": [
            TestCase(description="Standard sorted pair", call="two_sum_sorted([2, 7, 11, 15], 9)", expected=[1, 2]),
            TestCase(description="Negative and positive integers", call="two_sum_sorted([-3, 3, 4, 90], 0)", expected=[1, 2]),
            TestCase(description="Duplicate values summing to target", call="two_sum_sorted([2, 3, 4, 4], 8)", expected=[3, 4]),
            TestCase(description="Endpoints summing to target", call="two_sum_sorted([1, 2, 3, 4, 10], 11)", expected=[1, 5]),
            TestCase(description="Zero crossing array", call="two_sum_sorted([0, 0, 3, 4], 0)", expected=[1, 2])
        ],
        "hints": {
            1: {
                "title": "Sorted Order Invariant",
                "guidance": "Since the array is sorted, consider testing the extreme endpoints: `numbers[0]` and `numbers[-1]`. If their sum exceeds the target, which pointer must move to reduce the sum?",
                "question": "If `current_sum > target`, could moving `left` higher ever decrease the sum?"
            },
            2: {
                "title": "Boundary Convergence",
                "guidance": "Maintain `left = 0` and `right = len(numbers) - 1`. If `numbers[left] + numbers[right] < target`, increment `left`. Otherwise decrement `right`.",
                "question": "Did you remember that the problem requests 1-based index outputs (`left + 1`, `right + 1`)?"
            },
            3: {
                "title": "Scaffold",
                "guidance": """while left < right:
    s = numbers[left] + numbers[right]
    if s == target: return [left + 1, right + 1]
    elif s < target: left += 1
    else: right -= 1""",
                "question": "Does your loop safely exit if no solution exists?"
            }
        }
    },

    "longest_unique_substring": {
        "id": "longest_unique_substring",
        "title": "Sliding Window Unique Substring",
        "track": "Track 1: Algorithmic Invariants",
        "track_code": "ALG-102",
        "difficulty": "Medium",
        "summary": "Calculate length of longest substring without repeating characters in O(N) time.",
        "description": r"""### Problem Statement
Given a string `s`, find the length of the **longest substring** without duplicate characters.

### Examples
- `"abcabcbb"` -> `3` (the substring `"abc"`)
- `"bbbbb"` -> `1` (the substring `"b"`)
- `"pwwkew"` -> `3` (the substring `"wke"`)

### Algorithmic Constraint
A brute-force check of all substrings runs in $O(N^3)$. You must use a dynamic **sliding window** with a hash map of last-seen positions to achieve **O(N) time**.""",
        "constraints": [
            "0 <= len(s) <= 5 * 10^4",
            "s consists of English letters, digits, symbols and spaces",
            "Target Time Complexity: O(N)",
            "Target Space Complexity: O(min(M, N))"
        ],
        "starter_code": """def length_of_longest_substring(s: str) -> int:
    \"\"\"
    Calculate length of longest substring without duplicate characters in O(N).
    \"\"\"
    seen = {}
    max_len = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in seen and seen[char] >= start:
            start = seen[char] + 1
        seen[char] = end
        max_len = max(max_len, end - start + 1)
        
    return max_len
""",
        "test_cases": [
            TestCase(description="Multi-character repeats", call="length_of_longest_substring('abcabcbb')", expected=3),
            TestCase(description="Identical character sequence", call="length_of_longest_substring('bbbbb')", expected=1),
            TestCase(description="Overlapping internal substring", call="length_of_longest_substring('pwwkew')", expected=3),
            TestCase(description="Empty string boundary", call="length_of_longest_substring('')", expected=0),
            TestCase(description="Whitespace and symbols", call="length_of_longest_substring('tark ai 2026')", expected=9)
        ],
        "hints": {
            1: {
                "title": "Window Invariant",
                "guidance": "Think of the valid non-repeating substring as a window `[start...end]`. When encountering a duplicate character, where must `start` move?",
                "question": "Can `start` jump past the duplicate character's previous index without scanning intermediate characters?"
            },
            2: {
                "title": "Index Bounds Check",
                "guidance": "Store the last seen index in `seen[char]`. When `char in seen and seen[char] >= start`, jump `start = seen[char] + 1`.",
                "question": "Why is the condition `seen[char] >= start` necessary when examining historical characters?"
            },
            3: {
                "title": "Window Growth Loop",
                "guidance": """for end, char in enumerate(s):
    if char in seen and seen[char] >= start:
        start = seen[char] + 1
    seen[char] = end
    max_len = max(max_len, end - start + 1)
return max_len""",
                "question": "What is the amortized cost per character processed?"
            }
        }
    },

    "search_rotated_array": {
        "id": "search_rotated_array",
        "title": "Rotated Array Binary Search",
        "track": "Track 1: Algorithmic Invariants",
        "track_code": "ALG-103",
        "difficulty": "Medium",
        "summary": "Find target index in sorted rotated array in strictly O(log N) logarithmic time.",
        "description": r"""### Problem Statement
An integer array `nums` sorted in ascending order with distinct values is possibly rotated at an unknown pivot index (e.g. `[0,1,2,4,5,6,7]` might become `[4,5,6,7,0,1,2]`).

Given `nums` and a `target`, return the index of `target` if it is in `nums`, or `-1` if it is not.

### Strict Requirement
You must write an algorithm with **O(log N)** runtime complexity. Linear search ($O(N)$) is disallowed.""",
        "constraints": [
            "1 <= len(nums) <= 5000",
            "All values of nums are unique",
            "nums is guaranteed to be rotated at some pivot",
            "Strict Time: O(log N), Space: O(1)"
        ],
        "starter_code": """def search_rotated(nums: list[int], target: int) -> int:
    \"\"\"
    Search for target in rotated sorted array in O(log N) time.
    \"\"\"
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
            
        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
                
    return -1
""",
        "test_cases": [
            TestCase(description="Target in left sorted branch", call="search_rotated([4, 5, 6, 7, 0, 1, 2], 0)", expected=4),
            TestCase(description="Target not found in rotated array", call="search_rotated([4, 5, 6, 7, 0, 1, 2], 3)", expected=-1),
            TestCase(description="Single element match", call="search_rotated([1], 1)", expected=0),
            TestCase(description="Two elements rotated match", call="search_rotated([3, 1], 1)", expected=1),
            TestCase(description="Large rotated inflection", call="search_rotated([6, 7, 8, 1, 2, 3, 4, 5], 8)", expected=2)
        ],
        "hints": {
            1: {
                "title": "Half-Sorted Property",
                "guidance": "In any rotated sorted array, splitting at `mid` always divides the array into one normally sorted half and one rotated half. How can you determine which half is normally sorted?",
                "question": "If `nums[left] <= nums[mid]`, what can you guarantee about the subarray from `left` to `mid`?"
            },
            2: {
                "title": "Range Containment",
                "guidance": "Once you know which half is sorted, check whether `target` falls cleanly within the boundary of that sorted half (`nums[left] <= target < nums[mid]`). If yes, search that half; otherwise discard it.",
                "question": "Why does this guarantee discarding half the search space on each step?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "if nums[left] <= nums[mid]: check target in [nums[left], nums[mid]). Else: check target in (nums[mid], nums[right]].",
                "question": "What is the worst-case number of comparisons for 5000 elements?"
            }
        }
    },

    # -------------------------------------------------------------------------
    "sliding_window_max": {
        "id": "sliding_window_max",
        "title": "Sliding Window Maximum",
        "track": "Track 1: Algorithmic Invariants",
        "track_code": "ALG-104",
        "difficulty": "Hard",
        "summary": "Find the maximum element in sliding window of size k in strictly O(N) linear time using a monotonic deque.",
        "description": r"""### Problem Statement
You are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. Return the max sliding window array.

### Invariant
A naive approach takes $O(N \cdot k)$ time. By maintaining a **monotonically decreasing deque of indices**, we achieve strictly $O(N)$ time and $O(k)$ space.""",
        "constraints": [
            "1 <= len(nums) <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
            "1 <= k <= len(nums)",
            "Target Time Complexity: O(N)",
            "Target Space Complexity: O(k)"
        ],
        "starter_code": """from collections import deque

def max_sliding_window(nums: list[int], k: int) -> list[int]:
    q = deque()
    res = []
    
    for i, n in enumerate(nums):
        while q and q[0] <= i - k:
            q.popleft()
        while q and nums[q[-1]] < n:
            q.pop()
        q.append(i)
        if i >= k - 1:
            res.append(nums[q[0]])
    return res
""",
        "test_cases": [
            TestCase(description="Standard array k=3", call="max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)", expected=[3, 3, 5, 5, 6, 7]),
            TestCase(description="Single element array", call="max_sliding_window([1], 1)", expected=[1]),
            TestCase(description="Window equals array size", call="max_sliding_window([9, 11], 2)", expected=[11]),
            TestCase(description="Strictly decreasing elements", call="max_sliding_window([4, -2], 2)", expected=[4])
        ],
        "hints": {
            1: {
                "title": "Monotonic Deque Invariant",
                "guidance": "If element A is older than element B, and A < B, can element A ever be the maximum in any future window?",
                "question": "Why is it safe to pop smaller elements from the back of the deque?"
            },
            2: {
                "title": "Index Eviction",
                "guidance": "Store indices instead of values in the deque. The window boundary is i - k + 1.",
                "question": "How do you check if the element at the front of the deque has expired?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "Pop expired from left, pop smaller from right, append current index, append nums[q[0]] when i >= k - 1.",
                "question": "What is the total number of deque operations across the entire array?"
            }
        }
    },

    # TRACK 2: Core Data Structures & Invariants
    # -------------------------------------------------------------------------
    "valid_parentheses_stack": {
        "id": "valid_parentheses_stack",
        "title": "Syntax Bracket Validator (Stack)",
        "track": "Track 2: Data Structures & Invariants",
        "track_code": "DS-201",
        "difficulty": "Easy",
        "summary": "Verify matching brackets string using LIFO stack invariant in O(N) time.",
        "description": r"""### Problem Statement
Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

Open brackets must be closed by the same type of brackets in the correct LIFO order.""",
        "constraints": [
            "1 <= len(s) <= 10^4",
            "s consists of brackets only",
            "Time: O(N), Space: O(N)"
        ],
        "starter_code": """def is_valid_parentheses(s: str) -> bool:
    \"\"\"
    Validate bracket sequence using LIFO stack invariant.
    \"\"\"
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
            
    return not stack
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
                "title": "LIFO Invariant",
                "guidance": "The most recently opened bracket must be the first one closed. A stack provides $O(1)$ push and pop operations.",
                "question": "What should occur if you encounter a closing bracket while the stack is empty?"
            },
            2: {
                "title": "Closing Map",
                "guidance": "Map each closing bracket to its corresponding opening bracket: `mapping = {')': '(', '}': '{', ']': '['}`.",
                "question": "At the end of iteration, why must you assert `return not stack`?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "for c in s: if c in mapping: pop and compare. else: push c.",
                "question": "Can an odd-length string ever be valid?"
            }
        }
    },

    "monotonic_daily_temperatures": {
        "id": "monotonic_daily_temperatures",
        "title": "Monotonic Stack Next Greater Value",
        "track": "Track 2: Data Structures & Invariants",
        "track_code": "DS-202",
        "difficulty": "Medium",
        "summary": "Compute wait days until warmer temperature using monotonic decreasing stack in O(N).",
        "description": r"""### Problem Statement
Given an array of integers `temperatures` representing daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day with a warmer temperature, keep `answer[i] == 0`.

### Complexity Constraint
A naive nested loop takes $O(N^2)$. You must implement a **monotonic decreasing stack** to resolve this in **O(N) time and O(N) space**.""",
        "constraints": [
            "1 <= len(temperatures) <= 10^5",
            "30 <= temperatures[i] <= 100",
            "Time: O(N), Space: O(N)"
        ],
        "starter_code": """def daily_temperatures(temperatures: list[int]) -> list[int]:
    \"\"\"
    Compute wait days until warmer temperature using monotonic stack in O(N).
    \"\"\"
    n = len(temperatures)
    ans = [0] * n
    stack = []  # stores indices of unresolved temperatures
    
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            prev_idx = stack.pop()
            ans[prev_idx] = i - prev_idx
        stack.append(i)
        
    return ans
""",
        "test_cases": [
            TestCase(description="Ascending and descending days", call="daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])", expected=[1, 1, 4, 2, 1, 1, 0, 0]),
            TestCase(description="Monotonically increasing days", call="daily_temperatures([30, 40, 50, 60])", expected=[1, 1, 1, 0]),
            TestCase(description="Monotonically decreasing days", call="daily_temperatures([30, 60, 90])", expected=[1, 1, 0]),
            TestCase(description="All identical temperatures", call="daily_temperatures([70, 70, 70])", expected=[0, 0, 0])
        ],
        "hints": {
            1: {
                "title": "Unresolved Elements",
                "guidance": "Store indices of days whose warmer future day hasn't yet arrived on a stack. As soon as you see a warmer temperature, resolve all smaller elements currently waiting on the stack.",
                "question": "Why is storing indices more useful than storing raw temperature values?"
            },
            2: {
                "title": "Monotonic Invariant",
                "guidance": "The stack maintains indices with temperatures in strictly decreasing order. When `current_temp > temperatures[stack[-1]]`, pop and calculate `i - prev_idx`.",
                "question": "Since each index is pushed once and popped at most once, what is the amortized time complexity?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "while stack and temperatures[stack[-1]] < temp: prev = stack.pop(); ans[prev] = i - prev",
                "question": "What is the default value for days that never see a warmer temperature?"
            }
        }
    },

    # -------------------------------------------------------------------------
    # TRACK 3: Dynamic Programming & Recurrences
    # -------------------------------------------------------------------------
    "max_subarray_kadane": {
        "id": "max_subarray_kadane",
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "track": "Track 3: Dynamic Programming",
        "track_code": "DP-301",
        "difficulty": "Medium",
        "summary": "Find contiguous subarray with largest sum in single pass O(N) time and O(1) space.",
        "description": r"""### Problem Statement
Given an integer array `nums`, find the contiguous subarray with the largest sum and return its sum.

### Algorithmic Constraint
Must run in **O(N) time and O(1) space** with a single traversal using Kadane's dynamic invariant.""",
        "constraints": [
            "1 <= len(nums) <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
            "Time: O(N), Space: O(1)"
        ],
        "starter_code": """def max_sub_array(nums: list[int]) -> int:
    \"\"\"
    Compute max contiguous subarray sum in O(N) time and O(1) space.
    \"\"\"
    if not nums: return 0
    current_max = global_max = nums[0]
    
    for num in nums[1:]:
        current_max = max(num, current_max + num)
        global_max = max(global_max, current_max)
        
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
                "guidance": "At each step, decide whether to append `nums[i]` to the existing subarray or start a fresh subarray at `nums[i]`.",
                "question": "If your previous running sum dropped below 0, can adding it to `nums[i]` ever help?"
            },
            2: {
                "title": "State Transition",
                "guidance": "Transition: `current_max = max(num, current_max + num)`. Global update: `global_max = max(global_max, current_max)`.",
                "question": "Why must `global_max` be initialized to `nums[0]` rather than `0`?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "current_max = max(num, current_max + num); global_max = max(global_max, current_max)",
                "question": "How does this prove O(1) auxiliary memory?"
            }
        }
    },

    "coin_change_minimum": {
        "id": "coin_change_minimum",
        "title": "Coin Change Minimum (DP Tabulation)",
        "track": "Track 3: Dynamic Programming",
        "track_code": "DP-302",
        "difficulty": "Medium",
        "summary": "Compute fewest coins needed to make up amount using dynamic programming tabulation.",
        "description": r"""### Problem Statement
You are given an integer array `coins` representing coins of different denominations and an integer `amount`. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.

### Complexity Target
- Time Complexity: $O(N \times \text{amount})$
- Space Complexity: $O(\text{amount})$ using a 1D DP table.""",
        "constraints": [
            "1 <= len(coins) <= 12",
            "1 <= coins[i] <= 2^31 - 1",
            "0 <= amount <= 10^4"
        ],
        "starter_code": """def coin_change(coins: list[int], amount: int) -> int:
    \"\"\"
    Compute fewest coins to make up amount using bottom-up DP tabulation.
    \"\"\"
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for a in range(1, amount + 1):
        for c in coins:
            if a - c >= 0:
                dp[a] = min(dp[a], 1 + dp[a - c])
                
    return dp[amount] if dp[amount] != float('inf') else -1
""",
        "test_cases": [
            TestCase(description="Standard combination", call="coin_change([1, 2, 5], 11)", expected=3),
            TestCase(description="Impossible amount", call="coin_change([2], 3)", expected=-1),
            TestCase(description="Zero amount base case", call="coin_change([1], 0)", expected=0),
            TestCase(description="Exact coin match", call="coin_change([1, 5, 10], 10)", expected=1),
            TestCase(description="Greedy failure trap", call="coin_change([1, 6, 7, 9], 12)", expected=2)
        ],
        "hints": {
            1: {
                "title": "Why Greedy Fails",
                "guidance": "Picking the largest coin first fails on sets like `coins=[1, 6, 7, 9]` with `amount=12` (Greedy takes 9+1+1+1=4 coins, but 6+6=2 coins). Dynamic programming guarantees the global optimum.",
                "question": "What is the base case for `dp[0]`?"
            },
            2: {
                "title": "Bottom-Up Recurrence",
                "guidance": "For every amount `a` from `1` to `amount`, `dp[a] = min(dp[a], 1 + dp[a - coin])` for all coins where `a - coin >= 0`.",
                "question": "Why initialize the table with `float('inf')`?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "dp = [inf]*(amount+1); dp[0]=0; for a in 1..amount: for c in coins: if a-c>=0: dp[a] = min(dp[a], 1+dp[a-c])",
                "question": "What is the return expression if `dp[amount]` remains infinity?"
            }
        }
    },

    # -------------------------------------------------------------------------
    # TRACK 4: Production Python Systems & Concurrency
    # -------------------------------------------------------------------------
    "streaming_batch_generator": {
        "id": "streaming_batch_generator",
        "title": "Memory-Efficient Stream Batcher",
        "track": "Track 4: Production Systems",
        "track_code": "SYS-401",
        "difficulty": "Medium",
        "summary": "Build a generator yielding fixed-size batches from large iterables with zero RAM bloat.",
        "description": r"""### Problem Statement
In production data pipelines (e.g. streaming LLM tokens or bulk database operations), loading an entire iterable into memory causes $O(N)$ RAM spikes.

Write a generator function `batch_stream(iterable, batch_size)` that yields lists of at most `batch_size` items sequentially.

### Requirements
- Must be an authentic Python generator yielding batches lazily (`yield`).
- Do not call `len()` or slice `[:]` on the iterable.
- Memory complexity must be strictly $O(\text{batch\_size})$.
- Final batch may contain fewer items if input exhausts.""",
        "constraints": [
            "batch_size >= 1",
            "Memory complexity: O(batch_size), not O(N)",
            "Do not consume the iterable upfront"
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
                "guidance": "Using `yield` transforms your function into a generator iterator. Avoid converting the iterable to a list at the start.",
                "question": "What happens if the iterable is an infinite stream?"
            },
            2: {
                "title": "Buffer Reset",
                "guidance": "After yielding `batch`, assign `batch = []` to free memory references.",
                "question": "Did you remember to yield remaining elements after the loop finishes?"
            },
            3: {
                "title": "Scaffold",
                "guidance": "batch = []; for item in iterable: batch.append(item); if len(batch) == size: yield batch; batch = []; if batch: yield batch",
                "question": "What is the peak memory usage of this generator?"
            }
        }
    },

    "token_bucket_rate_limiter": {
        "id": "token_bucket_rate_limiter",
        "title": "Algorithmic Token Bucket Rate Limiter",
        "track": "Track 4: Production Systems",
        "track_code": "SYS-402",
        "difficulty": "Hard",
        "summary": "Implement a stateful Token Bucket rate limiter that handles token refills without sleep polling.",
        "description": r"""### Problem Statement
Implement a class `TokenBucketRateLimiter` that enforces API rate limits using the **Token Bucket algorithm**.

```python
limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_sec=2.0)
limiter.allow_request(tokens=1, current_time=0.0)  # -> True (4 tokens left)
```

### Invariant
Tokens must be replenished dynamically based on the elapsed time between requests (`elapsed * refill_rate_per_sec`) up to `capacity`. No background thread or sleep polling allowed.""",
        "constraints": [
            "capacity >= 1",
            "refill_rate_per_sec > 0",
            "O(1) execution time per request check"
        ],
        "starter_code": """class TokenBucketRateLimiter:
    \"\"\"
    Dynamic Token Bucket Rate Limiter without background threads.
    \"\"\"
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_sec)
        self.tokens = float(capacity)
        self.last_update = 0.0

    def allow_request(self, tokens: int = 1, current_time: float = 0.0) -> bool:
        # Refill tokens proportional to elapsed time
        elapsed = max(0.0, current_time - self.last_update)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = current_time
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
""",
        "test_cases": [
            TestCase(description="Initial burst allows requests", call="""(lambda: [
    (lim := TokenBucketRateLimiter(3, 1.0)).allow_request(1, 0.0),
    lim.allow_request(1, 0.0),
    lim.allow_request(1, 0.0),
    lim.allow_request(1, 0.0)
])()""", expected=[True, True, True, False]),
            TestCase(description="Refill after elapsed time", call="""(lambda: [
    (lim := TokenBucketRateLimiter(2, 2.0)).allow_request(2, 0.0),
    lim.allow_request(1, 0.0),
    lim.allow_request(1, 0.5)
])()""", expected=[True, False, True]),
            TestCase(description="Capacity ceiling respected", call="""(lambda: [
    (lim := TokenBucketRateLimiter(5, 10.0)).allow_request(1, 100.0),
    lim.tokens <= 5.0
])()""", expected=[True, True])
        ],
        "hints": {
            1: {
                "title": "Lazy Refill Invariant",
                "guidance": "Instead of running a background timer to add tokens every second, compute tokens lazily only when a request arrives: `added = (now - last_time) * rate`.",
                "question": "Why is lazy evaluation far more scalable than a background ticker thread for millions of users?"
            },
            2: {
                "title": "Capacity Bound",
                "guidance": "Tokens cannot exceed capacity: `self.tokens = min(self.capacity, self.tokens + added)`.",
                "question": "What happens if a user submits a timestamp smaller than `last_update`?"
            },
            3: {
                "title": "State Update",
                "guidance": "elapsed = current_time - self.last_update; self.tokens = min(self.capacity, self.tokens + elapsed * rate); self.last_update = current_time",
                "question": "How does this prevent race conditions in single-threaded async event loops?"
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
            track_code=c["track_code"],
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
