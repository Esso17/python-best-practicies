"""
================================================================================
MLOPS INTERVIEW EXERCISE #15 — Binary Search
================================================================================

STUDY CASE
----------
Binary search is ubiquitous in ML systems:

* Feature threshold search — find the optimal decision boundary in a sorted
  feature array (e.g., scanning for the lowest confidence threshold that still
  meets a precision target).
* Hyperparameter bisection — binary-search on learning rate, regularisation
  strength, or number of trees when each evaluation is expensive (budget-
  aware HPO).
* Model checkpoint lookup — given a sorted list of checkpoint timestamps or
  validation-loss values, quickly locate the best checkpoint to restore.
* Koko-style resource allocation — find the minimum batch-size / GPU memory
  limit that allows a training run to finish within a deadline (bisect-on-
  answer pattern).

KEY CONCEPTS
------------
1. Maintain a closed interval [lo, hi] and update carefully to avoid infinite
   loops and off-by-one errors.
2. Bisect-on-answer: binary-search on the *answer space* instead of an array
   index when a direct index doesn't exist.
3. For rotated arrays, one half is always sorted; use that fact to decide which
   half to discard.
4. Peak finding works because if nums[mid] < nums[mid+1], a peak exists to the
   right.

INTERFACES
----------

    binary_search(nums: list[int], target: int) -> int
        Standard binary search on a sorted array.
        Returns the index of target, or -1 if not present.
        Time: O(log n)  |  Space: O(1)

    first_occurrence(nums: list[int], target: int) -> int
        Return the leftmost index of target in sorted (possibly duplicate)
        array, or -1 if not found.
        Time: O(log n)  |  Space: O(1)

    last_occurrence(nums: list[int], target: int) -> int
        Return the rightmost index of target, or -1 if not found.
        Time: O(log n)  |  Space: O(1)

    search_rotated(nums: list[int], target: int) -> int
        Search target in a sorted array that has been rotated at an unknown
        pivot. Return index or -1.
        Time: O(log n)  |  Space: O(1)

    find_peak(nums: list[int]) -> int
        Return the index of *any* peak element (nums[i] > neighbours).
        Assume nums[-1] = nums[n] = -infinity.
        Time: O(log n)  |  Space: O(1)

    search_matrix(matrix: list[list[int]], target: int) -> bool
        2-D matrix where each row is sorted left-to-right and each column is
        sorted top-to-bottom (not necessarily globally sorted).
        Return True if target exists, False otherwise.
        Time: O(m + n)  |  Space: O(1)

    min_eating_speed(piles: list[int], h: int) -> int
        Koko bananas: return the minimum integer eating speed k such that Koko
        can eat all bananas in at most h hours.
        Time: O(n log max(piles))  |  Space: O(1)

    kth_smallest_in_matrix(matrix: list[list[int]], k: int) -> int
        n×n matrix where rows and columns are both sorted in ascending order.
        Return the k-th smallest element (1-indexed).
        Time: O(n log(max - min))  |  Space: O(1)

EXAMPLES
--------
>>> binary_search([1, 3, 5, 7, 9], 7)
3
>>> binary_search([1, 3, 5, 7, 9], 4)
-1

>>> first_occurrence([1, 2, 2, 2, 3], 2)
1
>>> last_occurrence([1, 2, 2, 2, 3], 2)
3

>>> search_rotated([4, 5, 6, 7, 0, 1, 2], 0)
4
>>> search_rotated([4, 5, 6, 7, 0, 1, 2], 3)
-1

>>> find_peak([1, 2, 3, 1])
2

>>> search_matrix([[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]], 5)
True
>>> search_matrix([[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]], 20)
False

>>> min_eating_speed([3, 6, 7, 11], 8)
4
>>> min_eating_speed([30, 11, 23, 4, 20], 5)
30

>>> kth_smallest_in_matrix([[1,5,9],[10,11,13],[12,13,15]], 8)
13
"""

from typing import List


def binary_search(nums: List[int], target: int) -> int:
    """Return index of target in sorted nums, or -1. O(log n)."""
    # TODO: maintain closed interval [lo, hi]
    # TODO: compute mid = lo + (hi - lo) // 2 to avoid overflow
    # TODO: return mid if match; shift lo or hi otherwise
    pass


def first_occurrence(nums: List[int], target: int) -> int:
    """Return leftmost index of target in sorted nums, or -1. O(log n)."""
    # TODO: standard binary search but when nums[mid] == target, record result
    #       and keep searching left (hi = mid - 1)
    pass


def last_occurrence(nums: List[int], target: int) -> int:
    """Return rightmost index of target in sorted nums, or -1. O(log n)."""
    # TODO: standard binary search but when nums[mid] == target, record result
    #       and keep searching right (lo = mid + 1)
    pass


def search_rotated(nums: List[int], target: int) -> int:
    """Search target in a rotated sorted array. Return index or -1. O(log n)."""
    # TODO: one of [lo..mid] or [mid..hi] is always sorted
    # TODO: use nums[lo] <= nums[mid] to identify the sorted half
    # TODO: check if target falls in the sorted half; narrow accordingly
    pass


def find_peak(nums: List[int]) -> int:
    """Return index of any peak element. Boundaries treated as -inf. O(log n)."""
    # TODO: if nums[mid] < nums[mid+1], peak is in right half (lo = mid + 1)
    # TODO: else peak is at mid or left (hi = mid)
    pass


def search_matrix(matrix: List[List[int]], target: int) -> bool:
    """Search sorted-row, sorted-col 2D matrix. O(m + n) staircase walk."""
    # TODO: start at top-right corner (row=0, col=n-1)
    # TODO: if val == target: return True
    # TODO: if val > target: move left (col -= 1)
    # TODO: if val < target: move down (row += 1)
    pass


def min_eating_speed(piles: List[int], h: int) -> int:
    """Return minimum integer eating speed k to finish all piles in h hours. O(n log max)."""
    # TODO: bisect on answer space [1, max(piles)]
    # TODO: feasibility: sum(math.ceil(pile / k) for pile in piles) <= h
    # TODO: if feasible, hi = mid; else lo = mid + 1
    pass


def kth_smallest_in_matrix(matrix: List[List[int]], k: int) -> int:
    """Return k-th smallest value (1-indexed) in n×n sorted matrix. O(n log(max-min))."""
    # TODO: binary search on value range [matrix[0][0], matrix[n-1][n-1]]
    # TODO: count_le(mid): staircase from bottom-left, count elements <= mid
    # TODO: if count_le(mid) >= k: hi = mid; else lo = mid + 1
    pass
