from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native330e78..330f08'):s.index('/* Native332194..332200')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
'''+body+r'''
int main(void){unsigned n=0;static const unsigned map[29]={0,4,6,7,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,27,28,29,30,32,33,34,35,36,37};for(unsigned pattern=0;pattern<256;pattern++)for(unsigned off=0;off<48;off++){_Alignas(4) uint8_t actual[128],expected[128];for(unsigned i=0;i<128;i++)actual[i]=(i*17+pattern);memcpy(expected,actual,128);expected[off]=25;for(unsigned i=1;i<29;i++)expected[off+i]=expected[64+map[i]];assert(opencfw_em9305_packet_event_fill_330e78((uintptr_t)(actual+off),(uintptr_t)(actual+64))==29);assert(memcmp(actual,expected,128)==0);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-fno-strict-aliasing','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('event-projection-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual29-byte C field projection, independent native byte mapping and overlapping destination fixtures. Host wide-read normalization does not prove native read timing/ISA/hardware.'},indent=2)+'\n');print('PASS',n)
