"""
Defines all helper functions that don't have a specific package.
"""
import copy

def get_all_subsets(items: set)->list:
    """
    Returns all possible subsets (including an empty subset).

    :param set items: set of all items
    :return set: set of all possible subsets
    """

    def recurse(current_set: set, leftovers: list):
        """
        fills result with all subsets for a given set and all items not yet passed.

        :param set current_set: set of items
        :param list leftovers: all elements not yet included
        :return:
        """
        print(current_set, leftovers)
        result.append(list(current_set))
        while leftovers:
            current = current_set.copy()
            current.add(leftovers.pop(0))
            recurse(current, leftovers.copy())

    work = list(items) # eases iterating through items uniformly.
    result = list() # add all subsets in this set

    recurse(set(), work)

    return sorted(result, key = lambda t : len(t))

