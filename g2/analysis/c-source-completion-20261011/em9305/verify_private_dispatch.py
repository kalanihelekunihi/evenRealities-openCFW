from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();body=s[s.index('/* Native32f494..'):s.index('extern uint32_t opencfw_em9305_ll_signed_apply_309aa4')]
body=body.replace('(uintptr_t)0x8016dcu','(uintptr_t)descriptor_data')
body=body.replace('(uintptr_t)0x805702u','(uintptr_t)&toggle').replace('(uintptr_t)0x80570eu','(uintptr_t)&setting').replace('uintptr_t source=0x805704u+offsets[i];','uintptr_t source=(uintptr_t)config+offsets[i];')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uint16_t cmd,setting;static uint8_t input[32],packet[48],expected[43],toggle;static _Alignas(4) uint8_t config[24];static uint8_t descriptor_data[28];static unsigned fail,sends,calls,expected_length;
static uint32_t pair(unsigned i){return input[i]+((uint32_t)input[i+1]<<8);}
static uint32_t sign(unsigned i){return input[i]&128?input[i]|0xffffff00u:input[i];}
static uint32_t child(void){calls++;return 0x91;}
uint32_t opencfw_em9305_ll_primary_send_32f794(uint32_t a,uint32_t b,uint32_t c){assert(cmd==0xffe4&&a==pair(0)&&b==pair(2)&&c==input[4]);return child();}
uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t p){assert(p==(uintptr_t)(input+2));return UINT64_C(0x76543210abcdef98);}
uint32_t opencfw_em9305_ll_private_mask_30d378(uint32_t a,uint32_t b,uint32_t c,uint32_t d){assert(cmd==0xffe7&&a==pair(0)&&b==0xabcdef98&&c==0x76543210&&d==(input[10]!=0));return child();}
uint32_t opencfw_em9305_ll_private_radio_30d8fc(uint32_t a,uint32_t b,uint32_t c){assert(cmd==0xffea&&a==input[0]&&b==sign(1)&&c==input[2]);return child();}
uint32_t opencfw_em9305_ll_private_signed_30cef0(uint32_t a,uint32_t b){assert(cmd==0xfff6&&a==pair(0)&&b==sign(2));return child();}
uint32_t opencfw_em9305_ll_private_signed_pair_30dd94(uint32_t a,uint32_t b,uint32_t c){assert(cmd==0xffdd&&a==pair(0)&&b==sign(2)&&c==input[3]);return child();}
uint32_t opencfw_em9305_ll_private_query_30bde0(uint32_t a,uintptr_t p){assert(cmd==0xffeb&&a==pair(0));uint8_t *b=(uint8_t*)p;assert(b[0]==2&&b[1]==0&&b[2]==0);b[0]=3;b[1]=4;b[2]=5;return child();}
uint32_t opencfw_em9305_ll_private_descriptor_303290(uintptr_t);
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(n==28);if(d!=packet+6){assert(s==descriptor_data);calls++;}return memcpy(d,s,n);}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(n==expected_length&&c==cmd);return fail?0:(uintptr_t)(packet+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet&&memcmp(packet+5,expected,43)==0);sends++;return 0;}
'''+body+r'''
static void reset(uint16_t c,unsigned pattern){cmd=c;for(unsigned i=0;i<28;i++)descriptor_data[i]=i+1;toggle=0x77;setting=0x7777;sends=calls=0;for(unsigned i=0;i<32;i++)input[i]=(uint8_t)(pattern?255-7*i:7*i);for(unsigned i=0;i<24;i++)config[i]=i+1;memset(packet,0xa5,48);memset(expected,0xa5,43);}
int main(void){unsigned cases=0;uint16_t cmds[]={0xffe3,0xffe4,0xffe5,0xffe7,0xffe9,0xffea,0xffeb,0xfff6,0xffdd,0xfffd};
for(unsigned k=0;k<10;k++)for(unsigned f=0;f<2;f++)for(unsigned pattern=0;pattern<2;pattern++){reset(cmds[k],pattern);fail=f;expected_length=k==4?17:k==6?4:k==9?29:1;unsigned haschild=k==1||k==3||k==5||k==6||k==7||k==8;expected[0]=haschild?0x91:0;if(k==4){unsigned offsets[]={0,4,12,16};for(unsigned i=0;i<4;i++)memcpy(expected+1+4*i,config+offsets[i],4);}if(k==6){expected[1]=3;expected[2]=4;expected[3]=5;}if(k==9)for(unsigned i=0;i<28;i++)expected[i+1]=i+1;
assert(opencfw_em9305_dispatch_32f494((uintptr_t)&cmd,(uintptr_t)input)==1&&sends==!f);assert(calls==haschild+(k==9&&!f));assert(toggle==(k==0?(input[0]!=0):0x77));assert(setting==(k==2?pair(0):0x7777));cases++;}
for(uint32_t c=0xffe3;c<=0xfff6;c++){if(c==0xffe3||c==0xffe4||c==0xffe5||c==0xffe7||c==0xffe9||c==0xffea||c==0xffeb||c==0xfff6)continue;reset(c,0);assert(opencfw_em9305_dispatch_32f494((uintptr_t)&cmd,(uintptr_t)input)==0&&calls==0&&sends==0);cases++;}printf("%u\n",cases);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['32f494..32f64c','303290..30329c'],'scope':'Actual selected C with normalized RAM and controlled genuine child contracts; native-reading routing/field checks, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-dispatch-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled private dispatcher cases')
