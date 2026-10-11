from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317280..3172c8'):s.index('/* Native309cfc..309e60')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','config_pointer').replace('*(volatile uint32_t *)(uintptr_t)0x805c3cu','base_pointer').replace('*(volatile uint32_t *)(row+180u)','host_association(row)')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t config[64],rows[512*256],associations[256][4];static uintptr_t config_pointer,base_pointer;static unsigned links;
static uintptr_t host_association(uintptr_t row){unsigned i=(row-base_pointer)/512;assert(i<256);return links?(uintptr_t)associations[i]:0;}
'''+b+r'''
int main(void){unsigned n=0;config_pointer=(uintptr_t)config;base_pointer=(uintptr_t)rows;
for(unsigned count=0;count<256;count++)for(unsigned id=0;id<258;id++)for(unsigned flags=0;flags<8;flags++){
 config[57]=count;links=flags&4;for(unsigned i=0;i<256;i++){rows[i*512]=flags&1;rows[i*512+3]=(flags&2)?1:2;associations[i][1]=i;}
 unsigned valid=(flags==7&&id<count);assert(opencfw_em9305_radio_association_exists_317280(id)==valid);n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('association-scan-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C allcountbytes/id0..257/active/state/nullassociation combinations. FixedRAM and32bit association pointer reads normalized; no native ISA/hardware execution.'},indent=2)+'\n');print('PASS',n)
