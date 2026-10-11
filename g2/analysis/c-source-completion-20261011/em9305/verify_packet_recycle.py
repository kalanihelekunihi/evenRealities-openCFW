from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31ae74..31ae84'):s.index('/* Native3183d4..3183ec')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uintptr_t expected;static unsigned calls;
uint32_t opencfw_em9305_wsf_queue_append(uintptr_t q,uintptr_t node){assert(q==0x8028c8&&node==expected);calls++;return 0x12345678;}
'''+b+r'''
int main(void){for(unsigned p=0;p<1024;p++){expected=(uintptr_t)p-8;calls=0;opencfw_em9305_radio_packet_complete_31ae74(p);assert(calls==1);}puts("1024");}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('packet-recycle-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C full forwarding/no added null guard, fixedqueue and eightbyte header subtraction. Realqueuechild normalized; pointer wrap is host width, nativeISA/hardware not executed.'},indent=2)+'\n');print('PASS',n)
