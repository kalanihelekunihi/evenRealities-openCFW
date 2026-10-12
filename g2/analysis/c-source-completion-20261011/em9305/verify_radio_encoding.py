from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();address=s[s.index('uintptr_t opencfw_em9305_radio_address_write_3045e8'):s.index('uintptr_t opencfw_em9305_radio_address_copy_304604')];b=s[s.index('/* Native3239d4'):s.index('extern uint32_t opencfw_em9305_radio_compose_323dc0')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
'''+address+b+r'''
static uint32_t rd(uint8_t *p,unsigned n){uint32_t x=0;for(unsigned i=0;i<n;i++)x|=(uint32_t)p[i]<<(8*i);return x;}
static void wr48(uint8_t *p,uint32_t lo,uint32_t hi){p[4]=hi;p[0]=lo;p[5]=hi>>8;p[3]=lo>>24;p[2]=lo>>16;p[1]=lo>>8;}
static void model(uint8_t *p,uint8_t *q){uint32_t hi=rd(q+4,4),lo=rd(q,4);wr48(p,lo,hi);hi=rd(q+12,4);lo=rd(q+8,4);wr48(p+6,lo,hi);uint32_t r0=rd(q+16,4),r1=rd(q+32,2),r2=r1>>8;p[12]=r0;r0=rd(q+16,4);p[13]=r0>>8;r0=rd(q+18,2);p[14]=r0;r0=q[19];p[15]=r0;r0=rd(q+20,4);p[16]=r0;r0=rd(q+20,4);p[17]=r0>>8;r0=rd(q+22,2);p[18]=r0;r0=q[38];p[19]=r0;r0=q[40];p[20]=r0;r0=q[41];p[23]=r2;p[22]=r1;p[21]=r0;p[24]=q[34];p[25]=q[35];p[26]=q[36];p[27]=q[37];p[28]=q[24];p[29]=q[25];p[30]=q[26];p[31]=q[27];p[32]=q[28];r0=q[43];r2=q[42];p[33]=(r0<<5)|r2;}
int main(void){unsigned cases=0;for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){uint8_t input[5]={a,c,(uint8_t)(a^c),(uint8_t)(a+c),(uint8_t)(a-c)},out[2];assert(opencfw_em9305_radio_encode_3239d4((uintptr_t)out,(uintptr_t)input)==2);assert(out[0]==(uint8_t)(input[0]|(input[1]<<5)|(input[2]<<6)|(input[3]<<7)));assert(out[1]==(uint8_t)(input[4]|(input[1]>>3)));cases++;}
for(unsigned seed=0;seed<256;seed++)for(unsigned offset=0;offset<=80;offset++){_Alignas(4) uint8_t actual[128],expected[128];for(unsigned i=0;i<128;i++)actual[i]=(uint8_t)(seed+i*37);memcpy(expected,actual,128);assert(opencfw_em9305_radio_encode_323c94((uintptr_t)(actual+offset),(uintptr_t)(actual+32))==34);model(expected+offset,expected+32);assert(memcmp(actual,expected,128)==0);cases++;}
printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('radio-encoding-host-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host actual C packed fields and full 34-byte serializer against native ordered-read/store model, overlapping aligned source with output offsets0..80. No ARC runtime or hardware proof.'},indent=2)+'\n');print('PASS',n)
