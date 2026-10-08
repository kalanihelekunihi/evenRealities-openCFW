"""Selected verbatim public completion helper; explicit synthetic type layout."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True);s=a.source.read_text();name='Cy_CapSense_ClrBusyFlags';match=re.search(r'void\s+'+name+r'\s*\([^;{]*\)\s*\{',s);start=match.start();i=match.end();depth=1
while depth:
 if s[i]=='{':depth+=1
 if s[i]=='}':depth-=1
 i+=1
prefix='''#include <stdint.h>
#include <stddef.h>
#define CY_CAPSENSE_BUSY_CH_MASK (0x01u)
#define CY_CAPSENSE_BUSY (0x80u)
typedef struct { uint8_t pad[8]; uint32_t status; } common_context;
typedef struct { void (*ptrSSCallback)(void *); void (*ptrEOSCallback)(void *); } internal_context;
typedef struct { void *ptrCommonConfig; common_context *ptrCommonContext; internal_context *ptrInternalContext; } cy_stc_capsense_context_t;
_Static_assert(offsetof(common_context,status)==8,"status offset");
_Static_assert(offsetof(internal_context,ptrEOSCallback)==4,"EOS offset");
_Static_assert(offsetof(cy_stc_capsense_context_t,ptrCommonContext)==4,"common offset");
_Static_assert(offsetof(cy_stc_capsense_context_t,ptrInternalContext)==8,"internal offset");
'''
c=a.output/'completion.c';c.write_text(prefix+s[start:i]+'\n');fw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:];stock=fw[0x614c-0x3300:0x6170-0x3300];rows=[]
for opt in ['Og','O1','O2','Os']:
 obj=a.output/(opt+'.o');subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-'+opt,'-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(c),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  e=ELFFile(f);data=e.get_section_by_name('.text.'+name).data();rel=e.get_section_by_name('.rel.text.'+name);rows.append({'optimization':opt,'stock_address':'0x614c','stock_extent':len(stock),'public_extent':len(data),'exact':data==stock,'relocations':rel.num_relocations() if rel else 0,'public_sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'matching_offsets':[hex(0x3300+k) for k in range(len(fw)-len(data)+1) if fw[k:k+len(data)]==data]})
receipt={'function':name,'pin':'247a9a0f79eb976f144f5fbeb29488c1c2606517','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'translation_unit_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'environment':prefix,'comparisons':rows,'limits':['Verbatim selected public function, explicit minimal ARM32 layout and macros; not a complete SDK build.','No uniquely identified producer compiler/release or callback-body claim.']};(D/'public-completion-screen.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(rows,indent=2))
