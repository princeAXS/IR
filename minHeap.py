import heapq

# Heap wrapper sourced from
# http://joernhees.de/blog/2010/07/19/min-heap-in-python/
# Minor modifications made for this IR assignment

class Heap(object):
    """ A neat min-heap wrapper which allows storing items by priority
        and get the lowest item out first (pop()).
        Also implements the iterator-methods, so can be used in a for
        loop, which will loop through all items in increasing priority order.
        Remember that accessing the items like this will iteratively call
        pop(), and hence empties the heap! """

    def __init__(self):
        """ create a new min-heap. """
        self._heap = []

    def push(self, priority, item, replace=False):
        """ Push an item with priority into the heap.
            Priority 0 is the highest, which means that such an item will
            be popped first."""
        assert priority >= 0

        # My little mod
        if replace and self._heap: # Remove smallest element simultaneously
            if priority > self._heap[0][0]: # Check this isn't going to be the smallest first
                heapq.heapreplace(self._heap, (priority, item)) # insert, removing _heap[0]
        else:
            heapq.heappush(self._heap, (priority, item)) # Otherwise just push (changes heap size)

    def pop(self):
        """ Returns the item with lowest priority. """
        item = heapq.heappop(self._heap)[1] # (prio, item)[1] == item
        return item

    def __len__(self):
        return len(self._heap)

    def __iter__(self):
        """ Get all elements ordered by asc. priority. """
        return self

    def next(self):
        """ Get all elements ordered by their priority (lowest first). """
        try:
            return self.pop()
        except IndexError:
            raise StopIteration