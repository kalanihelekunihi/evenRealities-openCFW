from pathlib import Path
import subprocess,tempfile,json,hashlib,re
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30e050 tail'):s.index('extern uint32_t opencfw_em9305_ll_test_schedule_first_31b7fc')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805c70u','((uintptr_t)primary)').replace('*(volatile uint32_t *)(uintptr_t)0x805b44u','0x87654321u').replace('*(volatile uint32_t *)(uintptr_t)0x805b40u','0x12345678u').replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)')
body=re.sub(r'__asm__ volatile\("mpyuw %0,%1,912":"=r"\(offset\):"r"\(index\)\);','offset=index*912u;',body)
body=re.sub(r'__asm__ volatile\("mpywhl %0,%1,%2":"=r"\(span\):"r"\(counter\),"r"\(stride\)\);','span=counter*stride;',body)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t link[656],stream[256],state_data[320],channel[140],primary[912],captured[36],request[36];static unsigned link_ok,stream_ok,submits,lookups;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(v==0&&n==36);return memset(p,v,n);}
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1122);lookups++;return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1122);lookups++;return stream_ok?(uintptr_t)stream:0;}
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){assert(id==9);return (uintptr_t)channel;}
uint32_t opencfw_em9305_ll_test_submit_31bb20(uintptr_t d,uintptr_t r,uint32_t context){assert(r==(uintptr_t)request&&context==(link_ok?0xabc12345:0x98765432));memcpy(captured,(void*)d,36);submits++;return 0xface;}
'''+body+r'''
int main(void){unsigned cases=0;for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned role=0;role<256;role++){for(unsigned parameter=0;parameter<256;parameter++){for(unsigned mode=0;mode<2;mode++){
 memset(request,0,36);memset(link,0,656);memset(stream,0,256);memset(state_data,0,320);*(uint16_t*)request=0x1122;request[2]=role;request[3]=parameter;
 link[10]=mode;link[11]=9;*(uint16_t*)(link+8)=0x3344;*(uint32_t*)(link+36)=0xffffffff;*(uint32_t*)(link+16)=0x11223344;*(uint32_t*)(link+492)=0xaabbccdd;*(uint32_t*)(link+496)=0x55667788;*(uint32_t*)(primary+516)=0x31415926;*(uint32_t*)(primary+520)=0x27182818;
 *(uint16_t*)(stream+2)=0x7788;state_data[3]=mode;*(uint32_t*)(state_data+16)=0xabcdef01;*(uint32_t*)(state_data+32)=9;state_data[24]=7;*(uint32_t*)(state_data+40)=0xfedcba98;
 *(uint32_t*)(channel+36)=0xabc12345;*(uint32_t*)(state_data+304)=0x98765432;submits=lookups=0;unsigned expected=parameter>=2&&parameter!=255?18:link_ok?(role<=1?0xface:12):!stream_ok?2:(role<=1&&mode==(role==0)?0xface:12);
 assert(opencfw_em9305_ll_test_30e050((uintptr_t)request)==expected&&submits==(expected==0xface));
 if(expected==0xface){uint8_t e[36]={0};*(uint16_t*)e=link_ok?0x3344:0x7788;e[2]=role;*(uint32_t*)(e+4)=link_ok?(mode?0x55667788:0xaabbccdd):0xabcdef01;*(uint32_t*)(e+8)=link_ok?0:70;*(uint32_t*)(e+12)=link_ok?0x11223344:0xfedcba98;*(uint32_t*)(e+16)=(uint32_t)(uintptr_t)(link_ok?link+(role?532:528):stream+(role?44:36));if(link_ok){*(uint32_t*)(e+(role?28:20))=0x12345678;*(uint32_t*)(e+(role?32:24))=0x87654321;*(uint32_t*)(e+(role?20:28))=0x31415926;*(uint32_t*)(e+(role?24:32))=0x27182818;}assert(memcmp(e,captured,36)==0);}cases++;
}}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-descriptor-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C descriptor body, controlled lookup/submit/fill children, normalized pointers and ISA arithmetic. Exhaustive role/parameter bytes with link/stream lookup alternatives and mode0/1; exact36B descriptor. Extra request4/16 rejection and link3 gate statically reconstructed, outside this fixture sweep. Not native ISA/runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
