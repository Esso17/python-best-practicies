"""
================================================================================
MLOPS INTERVIEW EXERCISE #15 — Binary Search  |  VALIDATE
================================================================================
Run: python validate.py
Each test prints PASSED or FAILED with an explanation on failure.
"""

import sys

sys.path.insert(0, ".")

try:
    from exercise import (
        binary_search,
        find_peak,
        first_occurrence,
        kth_smallest_in_matrix,
        last_occurrence,
        min_eating_speed,
        search_matrix,
        search_rotated,
    )
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

_PASS = 0
_FAIL = 0


def check(name: str, got, expected, extra: str = "") -> None:
    global _PASS, _FAIL
    if got == expected:
        print(f"  PASSED  {name}")
        _PASS += 1
    else:
        print(f"  FAILED  {name}")
        print(f"          got={got!r}  expected={expected!r}")
        if extra:
            print(f"          {extra}")
        _FAIL += 1


def check_peak(name: str, nums: list, idx: int) -> None:
    """Accept any valid peak index — just verify it dominates its neighbours."""
    global _PASS, _FAIL
    n = len(nums)
    left_ok = (idx == 0) or (nums[idx] >= nums[idx - 1])
    right_ok = (idx == n - 1) or (nums[idx] >= nums[idx + 1])
    if left_ok and right_ok:
        print(f"  PASSED  {name}")
        _PASS += 1
    else:
        print(f"  FAILED  {name}")
        print(f"          returned idx={idx!r}, nums[idx]={nums[idx]!r}")
        print(f"          array={nums}")
        _FAIL += 1


# ─────────────────────────────────────────────────────────────────────────────
print("\n── binary_search ────────────────────────────────────────────────────")
check("found — single element", binary_search([5], 5), 0)
check("found — first element", binary_search([1, 3, 5, 7, 9], 1), 0)
check("found — last element", binary_search([1, 3, 5, 7, 9], 9), 4)
check("found — middle element", binary_search([1, 3, 5, 7, 9], 5), 2)
check("found — index 3", binary_search([1, 3, 5, 7, 9], 7), 3)
check("not found — below range", binary_search([1, 3, 5, 7, 9], 0), -1)
check("not found — above range", binary_search([1, 3, 5, 7, 9], 10), -1)
check("not found — gap", binary_search([1, 3, 5, 7, 9], 4), -1)
check("empty array", binary_search([], 1), -1)
# With duplicates, any valid index is fine — just verify value matches
_nums_dup = [2, 2, 2, 2, 2]
_idx = binary_search(_nums_dup, 2)
check("duplicates — any valid index", _nums_dup[_idx] if _idx != -1 else -1, 2)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── first_occurrence ─────────────────────────────────────────────────")
check("single element found", first_occurrence([7], 7), 0)
check("no duplicates", first_occurrence([1, 3, 5, 7, 9], 5), 2)
check("first of duplicates", first_occurrence([1, 2, 2, 2, 3], 2), 1)
check("target at index 0", first_occurrence([2, 2, 2, 3, 4], 2), 0)
check("target at end", first_occurrence([1, 2, 3, 5, 5], 5), 3)
check("not found", first_occurrence([1, 2, 3, 4, 5], 6), -1)
check("empty", first_occurrence([], 1), -1)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── last_occurrence ──────────────────────────────────────────────────")
check("single element found", last_occurrence([7], 7), 0)
check("no duplicates", last_occurrence([1, 3, 5, 7, 9], 5), 2)
check("last of duplicates", last_occurrence([1, 2, 2, 2, 3], 2), 3)
check("target at index 0 only", last_occurrence([2, 3, 4, 5], 2), 0)
check("target at end", last_occurrence([1, 2, 3, 5, 5], 5), 4)
check("not found", last_occurrence([1, 2, 3, 4, 5], 6), -1)
check("empty", last_occurrence([], 1), -1)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── search_rotated ───────────────────────────────────────────────────")
check("target in right part", search_rotated([4, 5, 6, 7, 0, 1, 2], 0), 4)
check("target in left part", search_rotated([4, 5, 6, 7, 0, 1, 2], 6), 2)
check("not found", search_rotated([4, 5, 6, 7, 0, 1, 2], 3), -1)
check("single element found", search_rotated([1], 1), 0)
check("single element not found", search_rotated([1], 0), -1)
check("no rotation", search_rotated([1, 2, 3, 4, 5], 3), 2)
check("target at rotation pivot", search_rotated([6, 7, 1, 2, 3, 4, 5], 1), 2)
check("two elements rotated, found", search_rotated([2, 1], 1), 1)
check("two elements rotated, not found", search_rotated([2, 1], 3), -1)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── find_peak ────────────────────────────────────────────────────────")
# We check validity of the returned index, not the exact index
check_peak("ascending then descending", [1, 2, 3, 1], find_peak([1, 2, 3, 1]))
check_peak("peak at start", [3, 2, 1], find_peak([3, 2, 1]))
check_peak("peak at end", [1, 2, 3], find_peak([1, 2, 3]))
check_peak("single element", [5], find_peak([5]))
check_peak("two elements ascending", [1, 2], find_peak([1, 2]))
check_peak("two elements descending", [2, 1], find_peak([2, 1]))
check_peak("multiple peaks — any valid", [1, 3, 2, 4, 1], find_peak([1, 3, 2, 4, 1]))
check_peak(
    "MLOps: loss valleys / peaks",
    [5, 3, 1, 2, 4, 3, 6, 2],
    find_peak([5, 3, 1, 2, 4, 3, 6, 2]),
)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── search_matrix ────────────────────────────────────────────────────")
_M = [
    [1, 4, 7, 11],
    [2, 5, 8, 12],
    [3, 6, 9, 16],
    [10, 13, 14, 17],
]
check("found — interior", search_matrix(_M, 5), True)
check("found — top-left corner", search_matrix(_M, 1), True)
check("found — bottom-right corner", search_matrix(_M, 17), True)
check("found — top-right corner", search_matrix(_M, 11), True)
check("found — bottom-left corner", search_matrix(_M, 10), True)
check("not found — above max", search_matrix(_M, 20), False)
check("not found — gap value", search_matrix(_M, 15), False)
check("not found — below min", search_matrix(_M, 0), False)
check("empty matrix", search_matrix([], 5), False)
check("1x1 found", search_matrix([[7]], 7), True)
check("1x1 not found", search_matrix([[7]], 3), False)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── min_eating_speed ─────────────────────────────────────────────────")
check("example 1: [3,6,7,11] h=8 → 4", min_eating_speed([3, 6, 7, 11], 8), 4)
check(
    "example 2: [30,11,23,4,20] h=5 → 30", min_eating_speed([30, 11, 23, 4, 20], 5), 30
)
check(
    "example 3: [30,11,23,4,20] h=6 → 23", min_eating_speed([30, 11, 23, 4, 20], 6), 23
)
check("single pile h=1 → pile size", min_eating_speed([7], 1), 7)
check("single pile h=7 → 1", min_eating_speed([7], 7), 1)
check("all piles size 1 → 1", min_eating_speed([1, 1, 1, 1], 4), 1)
check(
    "MLOps: GPU memory bisect [8,4,16,2] h=4 → 16",
    min_eating_speed([8, 4, 16, 2], 4),
    16,
)

# ─────────────────────────────────────────────────────────────────────────────
print("\n── kth_smallest_in_matrix ───────────────────────────────────────────")
_MAT = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
check("k=1 (smallest)", kth_smallest_in_matrix(_MAT, 1), 1)
check("k=5", kth_smallest_in_matrix(_MAT, 5), 11)
check("k=8", kth_smallest_in_matrix(_MAT, 8), 13)
check("k=9 (largest)", kth_smallest_in_matrix(_MAT, 9), 15)
_MAT2 = [[1, 2], [3, 4]]
check("2x2 k=1", kth_smallest_in_matrix(_MAT2, 1), 1)
check("2x2 k=2", kth_smallest_in_matrix(_MAT2, 2), 2)
check("2x2 k=3", kth_smallest_in_matrix(_MAT2, 3), 3)
check("2x2 k=4", kth_smallest_in_matrix(_MAT2, 4), 4)
_MAT3 = [[1, 2], [1, 3]]
check("duplicates k=1", kth_smallest_in_matrix(_MAT3, 1), 1)
check("duplicates k=2", kth_smallest_in_matrix(_MAT3, 2), 1)
check("duplicates k=3", kth_smallest_in_matrix(_MAT3, 3), 2)

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print(f"  TOTAL  {_PASS + _FAIL}  |  PASSED {_PASS}  |  FAILED {_FAIL}")
if _FAIL:
    sys.exit(1)
