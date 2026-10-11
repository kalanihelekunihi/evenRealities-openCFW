from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331a8c..'):s.index('/* Native331a40..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805701u','pending_byte').replace('*(volatile uint8_t *)(uintptr_t)0x80585cu','handler_byte')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t pending_byte,handler_byte;static unsigned posts,kind,get_calls,accounts,status;static uintptr_t packet;static uint32_t input;
uintptr_t opencfw_em9305_ll_primary_pending_30853c(void){assert(kind==0);get_calls++;return packet;}
uintptr_t opencfw_em9305_ll_link_pending_30858c(void){assert(kind==1);get_calls++;return packet;}
uint32_t opencfw_em9305_ll_primary_account_331d60(uintptr_t p){assert(kind==0&&p==packet);accounts++;return status;}
uint32_t opencfw_em9305_ll_link_dispatch_331d94(uintptr_t p){assert(kind==1&&p==packet);accounts++;return status;}
uint32_t opencfw_em9305_ll_link_restart_308614(uint32_t credit){assert(credit==input);return credit^0x87654321;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t events){assert(handler==handler_byte&&events==8&&pending_byte==(uint8_t)input);posts++;return 0xcafebabe;}
'''+body+r'''
int main(void){unsigned count=0;for(kind=0;kind<2;kind++){for(unsigned present=0;present<2;present++){for(status=0;status<256;status++){
 packet=present?0x12345678:0;get_calls=accounts=0;uintptr_t actual=kind?opencfw_em9305_dispatch_331aa4():opencfw_em9305_dispatch_331a8c();assert(actual==(present&&status==0?packet:0)&&get_calls==1&&accounts==present);count++;
}}}
for(unsigned marker=0;marker<256;marker++){for(input=0;input<65536;input++){
 pending_byte=marker;handler_byte=input>>8;posts=0;uint32_t actual=opencfw_em9305_dispatch_331cbc(input|0xa5a50000);assert(actual==(marker?(input|0xa5a50000):0xcafebabe)&&posts==!marker&&pending_byte==(marker?marker:(uint8_t)input));count++;
}}
for(input=0;input<65536;input++){assert(opencfw_em9305_dispatch_331abc(input)==(input^0x87654321));count++;}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('pending-dispatch-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Four actual C dispatch bodies with normalized notification/handler cells and controlled selected children; empty/present packet versus allstatusbyte fixtures, fullword return vs lowbyte store, all pending/handler bytes, event write-before-post and credit/return forwarding. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
