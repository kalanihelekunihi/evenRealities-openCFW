# SPDX-License-Identifier: MIT
import unittest
from tools.analyze_gx8002_model_copy_ranges import inspect_copy,analyze_ranges
class CopyGeometryTests(unittest.TestCase):
    def geometry(self,source,destination,slot=1):
        return inspect_copy({'extents':[1,1,4],'source':{'base_slot':1,'offset':source},'destination':{'base_slot':slot,'offset':destination},'source_strides_elements':[4,4,1],'destination_strides_elements':[4,4,1]})
    def test_forward_overlap(self):self.assertEqual(self.geometry(0,2)['write_before_later_read'],[[0,1],[1,2],[2,3]])
    def test_backward_overlap(self):self.assertEqual(self.geometry(2,0)['write_before_later_read'],[])
    def test_odd_overlap(self):self.assertEqual(self.geometry(0,1)['write_before_later_read'],[[0,1],[1,2],[2,3]])
    def test_different_slot_not_assumed_alias(self):self.assertFalse(self.geometry(0,2,2)['same_slot'])
    def test_shipped_report(self):
        report=analyze_ranges();self.assertEqual(len(report['copy_commands']),123);self.assertEqual(report['hazardous_commands'],0)
        self.assertEqual(report['minimum_slot_bytes_from_copies'],{1:13056,3:8464,4:7424})
if __name__=='__main__':unittest.main()
