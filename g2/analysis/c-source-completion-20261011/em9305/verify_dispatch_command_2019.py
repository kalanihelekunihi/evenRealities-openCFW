from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW')
src=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=src.read_text();start=s.index('/* Native330568..3305ac:');body=s[start:s.index("/* Native332394..33248e:",start)]
harness=r'''
#include <stdint.h>
#include <assert.h>
extern uint32_t opencfw_em9305_dispatch_332278(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_332394(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t,uint32_t);
'''+body+r'''
static uintptr_t req,inp; static uint32_t calls,status,expected_id,expected_value;
uint32_t opencfw_em9305_dispatch_332278(uintptr_t r,uintptr_t i) { assert(r==req && i==inp);calls=2;return 73; }
uint32_t opencfw_em9305_dispatch_332394(uintptr_t r,uintptr_t i) { assert(r==req && i==inp);calls=3;return 91; }
uint32_t opencfw_em9305_ll_command_30e054(uint32_t id,uintptr_t a,uint32_t value,uintptr_t b) {
 assert(id==expected_id && value==expected_value && a==inp+2 && b==inp+12);assert(calls==0);calls=1;return status;
}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t s) { assert(r==req&&s==status&&calls==1);calls=4;return 0; }
int main(void) {
 uint16_t command;uint8_t bytes[28]={0};req=(uintptr_t)&command;inp=(uintptr_t)bytes;
 for(uint32_t n=0;n<4;n++) { command=0x2019;expected_id=n==3?65535:n*257;expected_value=65535-expected_id;bytes[0]=expected_id;bytes[1]=expected_id>>8;bytes[10]=expected_value;bytes[11]=expected_value>>8;status=n*17;calls=0;assert(opencfw_em9305_dispatch_330568(req,inp)==1);assert(calls==4); }
 command=0x2018;calls=0;assert(opencfw_em9305_dispatch_330568(req,inp)==73&&calls==2);
 calls=0;assert(opencfw_em9305_dispatch_3305ac(req,inp)==91&&calls==3);return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(harness)
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
receipt={'scope':'Actual selected C bodies isolated with controlled child contracts; source inference cases, not native emulation or hardware proof','cases_passed':6,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_ranges':['330568..3305ac','3305ac..3305b0'],'remaining_lower':'30e054 controller operation; 332278 and332394 dispatch children'}
out=root/'g2/analysis/c-source-completion-20261011/em9305'
(out/'dispatch-command-2019-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS6 selected C command contract cases; not native emulator proof')
