from pathlib import Path
import struct,json,hashlib
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=Path(Path('/tmp/opencfw-neg-model-path').read_text());raw=(r/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin').read_bytes();start=0x100150d8-0x10003000;b=raw[start:start+1024];a=list(struct.unpack('<256I',b));bs=[]
for v in a:
 lo=(0x8000-(v&0xffff))&0xffff;hi=(0-(v>>16))&0xffff
 signed=lo if lo<0x8000 else lo-0x10000
 abslo=min(abs(signed),0x7fff);bs.append(abslo|(hi<<16))
(d/'mac-corner-exclusion.json').write_text(json.dumps({'scope':'Three MAC instructions in authentic real-split assembly with real512/modifier1 table; not a universal C/compiler/other-callsite proof','table_sha256':hashlib.sha256(b).hexdigest(),'coefficient_pairs':256,'A_all_min_pair_indices':[i for i,v in enumerate(a) if v==0x80008000],'derived_B_all_min_pair_indices':[i for i,v in enumerate(bs) if v==0x80008000],'B_rule':'psub.16(Correction00008000,A), saturated-abs low signed16, pkg lowabs/highoriginal','B_low_lane_range_max':max(v&0xffff for v in bs),'source_mac_bindings':[{'source_line':65,'instruction':'mulaca.s16.s l0,t6,l2','coefficient_operand':'derivedB l2'},{'source_line':66,'instruction':'mulacax.s16.s l1,t4,t5','coefficient_operand':'tableA t5'},{'source_line':122,'instruction':'mulaca.s16.s t6,t1,t4','coefficient_operand':'tableA t4'}],'deduction':'Documented/QEMU extreme pair requires BOTH product operands80008000. At least one coefficient operand here cannot equal it. The specific all-min-pair corner is excluded for these table-bound paths, not all arithmetic model errors.'},indent=2)+'\n')
(d/'mac-corner-main.c').write_text('''typedef unsigned U;
extern U probe_mulaca(U,U,U),probe_mulacax(U,U,U);
static void text(char*s){while(*s)*(volatile U*)0x10003000=(unsigned char)*s++;}
static void hex(U x){int i;for(i=28;i>=0;i-=4)*(volatile U*)0x10003000="0123456789abcdef"[(x>>i)&15];}
int main(void){U z[]={0,0xffffffff,0x80000000},want[]={0x7fffffff,0x7fffffff,0};unsigned i;for(i=0;i<3;i++){text("z=");hex(z[i]);text(" manual=");hex(want[i]);text(" mulaca=");hex(probe_mulaca(0x80008000,0x80008000,z[i]));text(" mulacax=");hex(probe_mulacax(0x80008000,0x80008000,z[i]));text("\\n");}text("EXPECTED MODEL DISCREPANCY; not hardware validation\\n");return 0;}
''')
