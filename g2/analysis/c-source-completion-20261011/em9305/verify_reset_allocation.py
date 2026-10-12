from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native3253a4'):s.index('extern uint32_t opencfw_em9305_radio_prepare_state_32d694')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint32_t expected;static uintptr_t result;static unsigned calls;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t size){assert(size==expected);calls++;return result;}
'''+b+r'''
int main(void){unsigned cases=0;uintptr_t returns[]={0,0x805000,0xfffffffe,0xffffffff};for(unsigned n=0;n<65536;n++)for(unsigned hi=0;hi<2;hi++)for(unsigned r=0;r<4;r++){uint32_t size=n|(hi?0xffff0000u:0);expected=(size+12)&65535;result=returns[r];calls=0;assert(opencfw_em9305_radio_query_3253a4(size)==(result?(uint32_t)(result+2):0));assert(calls==1);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('reset-allocation-host-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host actual C full halfword size plus highword patterns, null/non-null/wrapping allocation pointer return. WSF child controlled; allocator/layout/runtime/hardware not proven.'},indent=2)+'\n');print('PASS',n)
