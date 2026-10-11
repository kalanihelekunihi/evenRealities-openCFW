from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30d9f4..'):s.index('/* Native313fc0..')]
body=body.replace('(void *)(uintptr_t)0x805b60u','(void *)key').replace('*(volatile uint8_t *)(uintptr_t)0x805b81u','active_byte').replace('*(volatile uint8_t *)(uintptr_t)0x805b83u','mode_byte')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t request[4],input_data[96],key[32],response_data[16];static uint8_t active_byte,mode_byte;static unsigned copies,allocations,sends,children,status_events,alloc_ok,mutate,initial_command;static uint32_t expected_status;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(d==key&&s==input_data&&n==32);copies++;memcpy(d,s,n);if(mutate)*(uint16_t*)request=0xbead;return d;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t length,uint32_t command){assert(length==1&&command==(copies&&mutate?0xbead:initial_command));allocations++;return alloc_ok?(uintptr_t)(response_data+5):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t event){assert(event==(uintptr_t)response_data&&response_data[5]==expected_status);sends++;return 99;}
uint32_t opencfw_em9305_ll_vendor_query_30bb10(void){assert(initial_command==0x2025);children++;return 0x12345678;}
uint32_t opencfw_em9305_ll_vendor_apply_30bad4(uintptr_t a,uintptr_t b,uint32_t n){assert(initial_command==0x205e&&a==(uintptr_t)input_data&&b==(uintptr_t)(input_data+32)&&n==77);children++;return 0x12345678;}
uint32_t opencfw_em9305_ll_vendor_apply_30baa0(uintptr_t a,uintptr_t b){assert(initial_command==0x2026&&a==(uintptr_t)input_data&&b==(uintptr_t)(input_data+32));children++;return 0x12345678;}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t status){assert(r==(uintptr_t)request&&status==0x12345678);status_events++;return 99;}
'''+body+r'''
int main(void){unsigned count=0;mutate=0;for(unsigned position=0;position<33;position++){for(unsigned value=0;value<256;value++){
 memset(input_data,0,96);memset(key,0xa5,32);if(position<32)input_data[position]=value;active_byte=42;copies=0;unsigned nonzero=position<32&&value;assert(opencfw_em9305_ll_vendor_key_30d9f4((uintptr_t)input_data)==0&&copies==nonzero&&active_byte==nonzero);if(nonzero)assert(memcmp(key,input_data,32)==0);else for(unsigned i=0;i<32;i++)assert(key[i]==0xa5);count++;
}}for(unsigned mode=0;mode<65536;mode++){mode_byte=42;assert(opencfw_em9305_ll_vendor_mode_30e040(mode)==(mode>1?18:0)&&mode_byte==(mode>1?42:mode));count++;}
for(initial_command=0;initial_command<65536;initial_command++){for(alloc_ok=0;alloc_ok<2;alloc_ok++){for(mutate=0;mutate<2;mutate++){
 *(uint16_t*)request=initial_command;memset(input_data,0,96);input_data[0]=initial_command&255;input_data[31]=1;input_data[64]=77;memset(key,0xa5,32);memset(response_data,0xa5,16);active_byte=42;mode_byte=42;copies=allocations=sends=children=status_events=0;expected_status=initial_command==0xffec&&(initial_command&255)>1?18:0;
 unsigned pre=initial_command==0xffe8||initial_command==0xffec,standard=initial_command==0x2025||initial_command==0x2026||initial_command==0x205e;
 assert(opencfw_em9305_dispatch_331aec((uintptr_t)request,(uintptr_t)input_data)==(pre||standard)&&copies==(initial_command==0xffe8)&&allocations==pre&&sends==(pre&&alloc_ok)&&children==standard&&status_events==standard);count++;
}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('vendor-dispatch-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual four C bodies, normalized key/active/mode cells; every16-bit command andmode value,32byte scan positions/values, allzero preserveskey, allocatorfail/success, requestcommand mutated bycopy and reloaded, exactstandard child arguments andstatus/response/send handling. Controlled children; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
