# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy
import sys
import struct
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import preserve_l8_resources as tool

class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.payload=struct.pack('<BBHHHHHIIII',25,6,0,3,2,3,0,6,0x101c,0,0)+bytes([0,1,10,13,128,255])
        self.spec={'payload_size':34,'payload_sha256':tool.digest(self.payload),'runtime_base':0x1000,'assets':[{'asset':'synthetic','descriptor_payload_range':[0,28],'descriptor_runtime':'0x1000','descriptor_sha256':tool.digest(self.payload[:28]),'pixel_payload_range':[28,34],'pixel_runtime_range':[0x101c,0x1022],'width':3,'height':2,'stride':3,'pixel_sha256':tool.digest(self.payload[28:])}]}
        self.input=self.root/'input.bin';self.input.write_bytes(self.payload)
    def export(self):
        d=self.root/'resources';tool.export(self.input,d,self.spec);return d
    def test_lossless_export_repack_binary_pixels(self):
        d=self.export();out=self.root/'repacked.bin';tool.repack(self.input,d,out,self.spec)
        self.assertEqual(out.read_bytes(),self.payload)
        self.assertEqual((d/'synthetic.pgm').read_bytes(),b'P5\n3 2\n255\n'+self.payload[28:])
        self.assertEqual(self.input.read_bytes(),self.payload)
    def test_missing_private_input_fails_without_output(self):
        d=self.root/'resources'
        with self.assertRaises(FileNotFoundError):tool.export(self.root/'missing',d,self.spec)
        self.assertFalse(d.exists())
    def test_tampered_pixels_and_pgm_rejected(self):
        d=self.export();out=self.root/'out'
        (d/'synthetic.l8').write_bytes(bytes(6))
        with self.assertRaises(ValueError):tool.repack(self.input,d,out,self.spec)
        self.assertFalse(out.exists())
        (d/'synthetic.l8').write_bytes(self.payload[28:]);(d/'synthetic.pgm').write_bytes(b'P5\n999 999\n255\n')
        with self.assertRaises(ValueError):tool.validate_resources(d,self.spec)
    def test_malformed_geometry_pointer_and_overlap(self):
        for offset,value in [(1,7),(8,4),(16,0x1020),(12,5)]:
            b=bytearray(self.payload)
            if offset==1:b[offset]=value
            elif offset==8:struct.pack_into('<H',b,offset,value)
            else:struct.pack_into('<I',b,offset,value)
            s=copy.deepcopy(self.spec);s['payload_sha256']=tool.digest(b);s['assets'][0]['descriptor_sha256']=tool.digest(b[:28])
            with self.subTest(offset=offset),self.assertRaises(ValueError):tool.validate_payload(bytes(b),s)
        s=copy.deepcopy(self.spec);a=copy.deepcopy(s['assets'][0]);a['asset']='duplicate';s['assets'].append(a)
        with self.assertRaises(ValueError):tool.validate_payload(self.payload,s)
    def test_wrong_input_hash_rejected(self):
        self.input.write_bytes(bytes(34))
        with self.assertRaises(ValueError):self.export()
    def test_existing_outputs_preserved(self):
        d=self.export()
        with self.assertRaises(ValueError):tool.export(self.input,d,self.spec)
        out=self.root/'out';out.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):tool.repack(self.input,d,out,self.spec)
        self.assertEqual(out.read_bytes(),b'keep')
    def test_fixed_provenance_map_loads(self):
        self.assertEqual(len(tool.load_map()['assets']),6)

if __name__=='__main__':unittest.main()
