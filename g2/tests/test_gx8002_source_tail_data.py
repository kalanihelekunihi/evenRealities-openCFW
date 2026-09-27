# SPDX-License-Identifier: MIT
import unittest
from tools.gx8002_source_tail_data import partition,sha

class TailDataTests(unittest.TestCase):
    def setUp(self):
        self.stock=bytes(range(64))
        self.host=dict(symbol='host',package_offset=16,bytes=32,compiled_bytes=16,
                       payload=b'C'*16+bytes(16),compiled_sha256=sha(b'C'*16),sha256=sha(self.stock[16:48]))
        self.data=dict(symbol='table',package_offset=32,bytes=16,compiled_bytes=16,
                       payload=b'D'*16,compiled_sha256=sha(b'D'*16),sha256=sha(self.stock[32:48]),ownership_kind='generated_source_data')
    def run_partition(self):
        return partition(self.stock,[self.host],self.data,'host',sha(self.stock[16:48]))
    def test_partition_preserves_code_and_separates_data(self):
        rows=self.run_partition()
        self.assertEqual([(r['package_offset'],r['bytes']) for r in rows],[(16,16),(32,16)])
        self.assertEqual(rows[0]['payload'],b'C'*16)
        self.assertEqual(self.host['bytes'],32)
    def test_partition_composes_with_existing_checksum_builder(self):
        from tools.build_gx8002_source_candidate import compose
        from tools.analyze_gx8002_upstream_objects import IMAGE
        stock=IMAGE.read_bytes();start=12772
        host=dict(self.host,package_offset=start,sha256=sha(stock[start:start+32]))
        data=dict(self.data,package_offset=start+16,sha256=sha(stock[start+16:start+32]))
        rows=partition(stock,[host],data,'host',host['sha256'])
        image,ownership,totals=compose(stock,rows)
        self.assertEqual(image[start:start+32],b'C'*16+b'D'*16)
        self.assertEqual(totals['compiled_c'],16)
        self.assertEqual(totals['generated_source_data'],4108)
        self.assertTrue(any(row['kind']=='generated_source_data' and row.get('symbol')=='table'
                            and row['size']==16 for row in ownership))
        self.assertEqual(totals['generated_unreachable_fill'],0)
        self.assertEqual(sum(totals.values()),len(stock))

    def test_code_overlap_rejected(self):
        self.data['package_offset']=28
        with self.assertRaisesRegex(ValueError,'exactly occupy'):self.run_partition()
    def test_changed_parent_identity_rejected(self):
        self.host['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'stock identity'):self.run_partition()
    def test_nonzero_fill_rejected(self):
        self.host['payload']=b'C'*16+b'X'*16
        with self.assertRaisesRegex(ValueError,'fill'):self.run_partition()
    def test_changed_data_payload_rejected(self):
        self.data['payload']=b'X'*16
        with self.assertRaisesRegex(ValueError,'payload identity'):self.run_partition()
    def test_executable_tail_rejected(self):
        self.data['ownership_kind']='compiled_c'
        with self.assertRaisesRegex(ValueError,'ownership'):self.run_partition()

if __name__=='__main__':unittest.main()
