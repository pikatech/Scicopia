from collections import Counter, deque
from typing import Iterator, List


class QuerySplitter:
    def __init__(self, ngrams: Counter) -> None:
        self.ngrams = ngrams

    def all_segmentations(query: List) -> Iterator[List[List]]:
        """
        Splits a collection of elements into all possible subsegments.

        E.g. Input = ['a','b','c']
            Output = [['a', 'b', 'c']]
                    [['a'], ['b', 'c']]
                    [['a', 'b'], ['c']]
                    [['a'], ['b'], ['c']]

        Parameters
        ----------
        query : List
            Any kind of indexable collection

        Yields
        -------
        Iterator[List[List]]
            All possible segmentations of the collection,
            so that the concatenation of the sublists of a split
            is identical to the original list of elements.
        """
        # Adapted from https://stackoverflow.com/questions/37023774/
        for cutpoints in range(1 << (len(query) - 1)):
            result = []
            lastcut = 0
            for i in range(len(query) - 1):
                if (1 << i) & cutpoints != 0:
                    result.append(query[lastcut : (i + 1)])
                    lastcut = i + 1
            result.append(query[lastcut:])
            yield result

    def segment_query(self, query: List[str]) -> List[str]:
        """
        Find the best possible split of a query into its constituting
        terms by applying n-gram weighting to all possible combinations
        of splits.

        Parameters
        ----------
        query : str
            The query as entered by the user

        Returns
        -------
        List[str]
            The best seqmentation of a query according to its score
        """
        best_score = 0
        best_partition = query
        for partition in QuerySplitter.all_segmentations(query):
            score = 0
            for element in partition:
                if 2 <= len(element) <= 5:
                    score += (
                        len(element) ** len(element) * self.ngrams[" ".join(element)]
                    )
            if score > best_score:
                best_score = score
                best_partition = partition
        return best_partition

    def process_terms(self, terms: deque):
        queries = []
        # Anything to disambiguate at all?
        if terms:
            counter, term = terms.popleft()
            subquery = [term]
        else:
            return queries
        for index, term in terms:
            # Consecutive segment
            if index == counter + 1:
                counter += 1
                subquery.append(term)
            else:
                # Degenerate case
                if len(subquery) == 1:
                    queries.append({"multi_match": {"query": subquery[0]}})
                else:
                    segments = self.segment_query(subquery)
                    for segment in segments:
                        if isinstance(segment, str):
                            queries.append({"multi_match": {"query": segment}})
                        else:
                            queries.append({"multi_match": {"query": " ".join(segment), "type": "phrase"}})
                counter = index
                subquery = [term]
        if len(subquery) == 1:
            queries.append({"multi_match": {"query": subquery[0]}})
        else:
            segments = self.segment_query(subquery)
            for segment in segments:
                if isinstance(segment, str):
                    queries.append({"multi_match": {"query": segment}})
                else:
                    queries.append({"multi_match": {"query": " ".join(segment), "type": "phrase"}})
        return queries
