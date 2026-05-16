"""
================================================================================
MLOPS INTERVIEW EXERCISE #15 — Binary Search  |  SOLUTION
================================================================================
Production-grade implementations with complexity annotations.
"""

import math
from typing import List


# ─────────────────────────────────────────────────────────────────────────────
# binary_search
# Time:  O(log n)  —  halve search space every iteration
# Space: O(1)      —  two pointers only
# ─────────────────────────────────────────────────────────────────────────────
def binary_search(nums: List[int], target: int) -> int:
    """Return index of target in sorted nums, or -1."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (
            lo + (hi - lo) // 2
        )  # avoid overflow (relevant in C/Java; harmless in Python)
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ─────────────────────────────────────────────────────────────────────────────
# first_occurrence  (left-biased binary search)
# Time:  O(log n)
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def first_occurrence(nums: List[int], target: int) -> int:
    """Return leftmost index of target in sorted nums, or -1."""
    lo, hi = 0, len(nums) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            result = mid  # record candidate, keep searching left
            hi = mid - 1
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result


# ─────────────────────────────────────────────────────────────────────────────
# last_occurrence  (right-biased binary search)
# Time:  O(log n)
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def last_occurrence(nums: List[int], target: int) -> int:
    """Return rightmost index of target in sorted nums, or -1."""
    lo, hi = 0, len(nums) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            result = mid  # record candidate, keep searching right
            lo = mid + 1
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result


# ─────────────────────────────────────────────────────────────────────────────
# search_rotated
# Key insight: one of the two halves [lo..mid] or [mid..hi] is always sorted.
# Use that sorted half to determine if target belongs there; otherwise search
# the other half.
# Time:  O(log n)
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def search_rotated(nums: List[int], target: int) -> int:
    """Search target in rotated sorted array. Return index or -1."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        # Left half is sorted
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


# ─────────────────────────────────────────────────────────────────────────────
# find_peak
# Key insight: if nums[mid] < nums[mid+1], the right side is "going up" so a
# peak must exist there (or at mid+1 itself). Otherwise look left (including mid).
# Boundaries are treated as -infinity so the first/last element can be peaks.
# Time:  O(log n)
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def find_peak(nums: List[int]) -> int:
    """Return index of any peak element (nums[i] >= neighbours)."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1  # ascending — peak is to the right
        else:
            hi = mid  # descending or plateau — peak is at mid or to the left
    return lo


# ─────────────────────────────────────────────────────────────────────────────
# search_matrix  (staircase / elimination walk)
# Start at top-right corner.  Each comparison eliminates an entire row or column.
# Time:  O(m + n)  where m = rows, n = cols
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def search_matrix(matrix: List[List[int]], target: int) -> bool:
    """Search sorted-row, sorted-col 2D matrix. Return True if found."""
    if not matrix or not matrix[0]:
        return False
    row, col = 0, len(matrix[0]) - 1  # start at top-right
    while row < len(matrix) and col >= 0:
        val = matrix[row][col]
        if val == target:
            return True
        elif val > target:
            col -= 1  # current value too large — move left
        else:
            row += 1  # current value too small — move down
    return False


# ─────────────────────────────────────────────────────────────────────────────
# min_eating_speed  (bisect-on-answer / Koko bananas)
# Binary search on speed k in [1, max(piles)].
# For a given k, hours needed = sum(ceil(pile / k)) for each pile.
# Feasibility: total_hours <= h.
# Time:  O(n log(max(piles)))
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def min_eating_speed(piles: List[int], h: int) -> int:
    """Return minimum integer eating speed k to finish all piles in h hours."""

    def feasible(k: int) -> bool:
        return sum(math.ceil(pile / k) for pile in piles) <= h

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid  # mid works — try slower
        else:
            lo = mid + 1  # too slow — need to eat faster
    return lo


# ─────────────────────────────────────────────────────────────────────────────
# kth_smallest_in_matrix
# Binary search on the value range [matrix[0][0], matrix[n-1][n-1]].
# count_le(mid): count elements <= mid using the staircase walk (O(n) per call).
# Invariant: lo is always a value that exists in the matrix.
# Time:  O(n log(max - min))
# Space: O(1)
# ─────────────────────────────────────────────────────────────────────────────
def kth_smallest_in_matrix(matrix: List[List[int]], k: int) -> int:
    """Return k-th smallest value (1-indexed) in n×n sorted matrix."""
    n = len(matrix)

    def count_le(mid: int) -> int:
        """Count elements <= mid using staircase from bottom-left."""
        count = 0
        row, col = n - 1, 0  # start at bottom-left
        while row >= 0 and col < n:
            if matrix[row][col] <= mid:
                count += row + 1  # all elements in this column up to current row
                col += 1
            else:
                row -= 1
        return count

    lo, hi = matrix[0][0], matrix[n - 1][n - 1]
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if count_le(mid) >= k:
            hi = mid  # mid might be the answer — don't discard it
        else:
            lo = mid + 1
    return lo
