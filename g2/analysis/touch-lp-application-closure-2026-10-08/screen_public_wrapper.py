"""Compile selected pinned public all-LP wrapper with resolved stock call target."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True);s=a.source.read_text();name='Cy_CapSense_ScanAllLpSlots';m=re.search(r'cy_capsense_status_t\s+'+name+r'\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
while depth:
 if s[i]=='{':depth+=1
 if s[i]=='}':depth-=1
 i+=1
prefix='''#include <stdint.h>
#include <stddef.h>
typedef uint32_t cy_capsense_status_t;
typedef void cy_stc_capsense_context_t;
#define CY_CAPSENSE_STATUS_BAD_PARAM 1u
#define CY_CAPSENSE_SLOT_LP_COUNT 4u
cy_capsense_status_t Cy_CapSense_ScanLpSlots(uint32_t,uint32_t,cy_stc_capsense_context_t *);
''';c=a.output/'wrapper.c';c.write_text(prefix+s[m.start():i]+'\n');link=a.output/'link.ld';link.write_text('Cy_CapSense_ScanLpSlots = 0x6d75; SECTIONS { .text 0x7050 : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');raw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:];stock=raw[0x7050-0x3300:0x7064-0x3300];rows=[]
for opt in ['Og','O1','O2','Os']:
 elf=a.output/(opt+'.elf');subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-'+opt,'-ffreestanding','-fno-builtin','-nostdlib','-T',str(link),str(c),'-o',str(elf)],check=True)
 with elf.open('rb') as f:data=ELFFile(f).get_section_by_name('.text').data()
 rows.append({'optimization':opt,'extent':len(data),'stock_extent':len(stock),'exact':data==stock,'stock_sha256':hashlib.sha256(stock).hexdigest(),'public_sha256':hashlib.sha256(data).hexdigest(),'matching_addresses':[hex(0x3300+k) for k in range(len(raw)-len(data)+1) if raw[k:k+len(data)]==data]})
(D/'public-wrapper-screen.json').write_text(json.dumps({'function':name,'pin':'247a9a0f79eb976f144f5fbeb29488c1c2606517','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'environment':prefix,'translation_unit_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'resolved_external_call':'Cy_CapSense_ScanLpSlots=0x6d75; actual firmware body, not supplied vendor rebuild','comparisons':rows,'limits':['Selected wrapper with explicit opaque context/macro environment and fixed resolved peer address; not full SDK build.','No peer byte-attribution or unique producer/compiler identification.']},indent=2)+'\n');print([(r['optimization'],r['exact'],r['extent']) for r in rows])
