"""Extract authenticated bootloader initializer records; do not execute targets."""
from pathlib import Path
import hashlib,json,struct,argparse
ROOT=Path(__file__).resolve().parents[5]
LOCKED_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BASE=0x410000
KNOWN={0x4301d7:'platform sequence',0x43194d:'services',0x415591:'redirect',0x41fd71:'allocator'}
def extract(blob,begin=0x433440,end=0x433460):
 if hashlib.sha256(blob).hexdigest()!=LOCKED_SHA:raise ValueError('locked bootloader identity mismatch')
 if begin<BASE or end<begin or end>BASE+len(blob) or (end-begin)%8:raise ValueError('invalid initializer record extent')
 raw_count=(end-begin)//8;count=min(raw_count,256);rows=[]
 for i in range(count):
  address=begin+8*i;callback,priority=struct.unpack_from('<II',blob,address-BASE)
  rows.append({'record_address':hex(address),'callback_thumb_address':hex(callback),'priority':priority,'known_role':KNOWN.get(callback),'target_present_in_ota':BASE<= (callback&~1)<BASE+len(blob) if callback else False})
 return {'raw_record_count':raw_count,'runner_capped_count':count,'records':rows,'record_bytes_sha256':hashlib.sha256(blob[begin-BASE:begin-BASE+8*count]).hexdigest(),'limits':['Records are call targets and priority metadata, not decompiler/source completeness. Runner skips zero callbacks.','Stock comparator returns signed low32(left.priority-right.priority); arbitrary unsigned sorting must not substitute for its behavior. Existing init_table/qsort source has original-instruction tests.']}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--image',type=Path,default=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin');ap.add_argument('--begin',type=lambda x:int(x,0),default=0x433440);ap.add_argument('--end',type=lambda x:int(x,0),default=0x433460);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 d={'status':'PASS','image_sha256':LOCKED_SHA,'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'load_address':hex(BASE),'table_begin':hex(args.begin),'table_end':hex(args.end),'result':extract(args.image.read_bytes(),args.begin,args.end)};args.output.write_text(json.dumps(d,indent=2)+'\n');print('PASS',d['result']['runner_capped_count'],'initializer records')
if __name__=='__main__':main()
