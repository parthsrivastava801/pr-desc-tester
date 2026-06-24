import unittest
from pagination import paginate_queryset

class PaginationTestCase(unittest.TestCase):
    def test_paginate_queryset(self):
        queryset = list(range(1, 26))  # 25 items
        
        # Test page 1
        res = paginate_queryset(queryset, page=1, page_size=10)
        self.assertEqual(res['total_pages'], 3)
        self.assertEqual(len(res['results']), 10)
        self.assertEqual(res['results'][0], 1)
        
        # Test page 3 (last page)
        res3 = paginate_queryset(queryset, page=3, page_size=10)
        self.assertEqual(res3['total_pages'], 3)
        self.assertEqual(len(res3['results']), 5)
        self.assertEqual(res3['results'][-1], 25)

if __name__ == '__main__':
    unittest.main()
