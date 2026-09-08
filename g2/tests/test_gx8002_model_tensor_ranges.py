# SPDX-License-Identifier: MIT
import unittest
from tools.analyze_gx8002_model_tensor_ranges import geometry,report
class TensorRangesTests(unittest.TestCase):
    def test_broadcast(self):
        t={'extents':[2,3,4]}
        for role,strides in (('source_a',[12,4,1]),('source_b',[0,0,1]),('destination',[20,5,1])):
            t[role]={'base_slot':1,'offset':100};t[role+'_strides_elements']=strides
        g=geometry(t)
        self.assertEqual(g['source_a']['end_exclusive'],148)
        self.assertEqual(g['source_b']['end_exclusive'],108)
        self.assertEqual(g['destination']['end_exclusive'],168)
    def test_shipped_weight_extent(self):
        r=report();self.assertEqual(len(r['commands']),29)
        self.assertEqual(r['minimum_slot_bytes_from_tensor_ops'][6],120800)
if __name__=='__main__':unittest.main()
