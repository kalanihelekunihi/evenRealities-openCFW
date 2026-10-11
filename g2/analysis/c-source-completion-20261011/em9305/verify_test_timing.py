from pathlib import Path
import subprocess,tempfile,json,hashlib,re
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c728 tail'):s.index('extern uint32_t opencfw_em9305_ll_test_action_31b7e4')]
body=body.replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)')
body=re.sub(r'__asm__ volatile\("mpyw %0,%1,%2":"=r"\((\w+)\):"r"\((\w+)\),"r"\((\w+)\)\);',r'\1=\2*\3;',body)
body=re.sub(r'__asm__ volatile\("mpywhl %0,%1,%2":"=r"\((\w+)\):"r"\((\w+)\),"r"\((\w+)\)\);',r'\1=\2*(uint32_t)(int32_t)(int16_t)\3;',body)
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t link[656],stream[256],state_data[320],channel[64],output[16],expected_channel[64],expected_output[16];static unsigned link_ok,stream_ok;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==7);return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==7);return stream_ok?(uintptr_t)stream:0;}
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){assert(id==73);return (uintptr_t)channel;}
'''+body+r'''
int main(void){unsigned cases=0;unsigned phases[]={0,1,2,255},kinds[]={0,1,255},strides[]={0,1,127,255},periods[]={0,1,65535,65536};
for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned mode=0;mode<4;mode++){for(unsigned gates=0;gates<8;gates++){for(unsigned phase=0;phase<4;phase++){for(unsigned kind=0;kind<3;kind++){for(unsigned ready=0;ready<2;ready++){for(unsigned remaining=0;remaining<2;remaining++){for(unsigned counter=0;counter<4;counter++){for(unsigned alias=0;alias<4;alias++){
 memset(link,0,656);memset(stream,0,256);memset(state_data,0,320);memset(channel,0,64);memset(output,0xa5,16);link[11]=73;link[10]=mode;link[512]=(gates&1)!=0;link[513]=(gates&2)!=0;link[624]=(gates&4)!=0;*(uint16_t*)(link+14)=periods[counter];state_data[3]=kinds[kind];state_data[30]=phases[phase];stream[32]=ready;*(uint32_t*)(state_data+36)=remaining;*(uint32_t*)(state_data+32)=periods[counter];*(uint32_t*)(state_data+16)=0x2000;*(uint32_t*)(state_data+304)=0x1000+counter*17;state_data[24]=strides[counter];*(uint16_t*)(channel+20)=24;*(uint32_t*)(channel+48)=0xabcdef00;memcpy(expected_channel,channel,64);memcpy(expected_output,output,16);
 uint8_t *first=alias==2?channel+20:alias==1?output+4:output,*efirst=alias==2?expected_channel+20:alias==1?expected_output+4:expected_output;uint8_t *third=output+(alias==3?4:8),*ethird=expected_output+(alias==3?4:8);unsigned status;
 if(link_ok){status=mode<2&&!(gates&(1u<<mode))?12:!(gates&4)?12:0;if(!status){unsigned stride=mode==0?((gates&1)!=0):((gates&2)!=0);*(uint16_t*)efirst=(uint16_t)((periods[counter]-1)*stride);uint32_t value=(uint32_t)-1250*(*(uint16_t*)(expected_channel+20))+0xabcdef00;*(uint32_t*)(expected_output+4)=value;*(uint32_t*)ethird=0;}}
 else if(!stream_ok)status=2;
 else {status=kinds[kind]!=1?12:phases[phase]==1&&!ready?17:phases[phase]>1?17:phases[phase]==0&&!(remaining|periods[counter])?12:0;if(!status){uint32_t span=(periods[counter]-1)*strides[counter],value=(uint32_t)(0xfffff000u+counter*17)*strides[counter];if(phases[phase]==1){*(uint32_t*)(expected_output+4)=value;*(uint16_t*)efirst=span;}else{*(uint16_t*)efirst=span;*(uint32_t*)(expected_output+4)=value;}*(uint32_t*)ethird=0;}}
 assert(opencfw_em9305_ll_test_30c728(7,(uintptr_t)first,(uintptr_t)(output+4),(uintptr_t)third)==status);assert(memcmp(output,expected_output,16)==0&&memcmp(channel,expected_channel,64)==0);cases++;
}}}}}}}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-timing-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with normalized runtime state pointer and MPYW/MPYWHL products, controlled selected lookup children. Link/stream gates, error preservation, phase-specific output alias ordering and channel reload after output write. Target source retains named native multiplication; this harness is not native ISA/runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
