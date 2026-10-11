from pathlib import Path
import subprocess,tempfile,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('extern uint32_t opencfw_em9305_command_apply_3093a0'):s.index('/* Native3098ac')];b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?"r"\(groups\),"r"\(unit\)\);','product=groups*unit;',b);b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?"r"\(factor\),"r"\(extra\)\);','product=factor*extra;',b)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static unsigned calls,gate;
uint32_t opencfw_em9305_command_apply_3093a0(uint32_t k,uintptr_t p){assert(k==7&&p);calls++;return 91;}
uint32_t opencfw_em9305_command_apply_309514(uint32_t id,uint32_t i,uint32_t a,uint32_t b,uint32_t c,uint32_t n,uintptr_t p){assert(id<=3839&&i==0x12345678&&a<15&&b<15&&c==0xffffffff&&n<=251&&p==7);calls++;return 92;}
uint32_t opencfw_em9305_command_apply_3098ac(uint32_t id,uint32_t flags,uint32_t n,uintptr_t p){assert(id==7&&!(flags&0xffbf)&&n==4&&p);calls++;return 93;}
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
'''+b+r'''
int main(void){unsigned cases=0;for(unsigned id=3838;id<3842;id++)for(unsigned a=0;a<17;a++)for(unsigned n=250;n<254;n++){calls=0;unsigned ok=id<=3839&&a<15&&n<=251;assert(opencfw_em9305_command_30dc20(id,0x12345678,a,a,0xffffffff,n,7)==(ok?92:18)&&calls==ok);cases++;}uint8_t list[4]={0,14,1,2};for(unsigned flags=0;flags<65536;flags++)for(unsigned last=0;last<17;last++){list[3]=last;calls=0;unsigned ok=!(flags&0xffbf)&&last<15;assert(opencfw_em9305_command_30dccc(7,flags,4,(uintptr_t)list)==(ok?93:18)&&calls==ok);cases++;}
_Alignas(4) uint8_t input[12]={0};*(uint16_t *)input=6;*(uint16_t *)(input+2)=100;for(gate=0;gate<2;gate++)for(unsigned g=0;g<17;g++)for(unsigned unit=0;unit<17;unit++)for(unsigned off=0;off<17;off++){input[6]=g;input[7]=unit;input[8]=off;input[9]=3;input[10]=2;calls=0;unsigned ok=g<16&&(g==0||(unit>=6&&100>=g*unit&&off!=0&&off<unit&&(unit-off)*10>=6));unsigned expected=!gate?12:ok?91:18;assert(opencfw_em9305_command_30db64(7,(uintptr_t)input)==expected&&calls==(gate&&ok));cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('command-children-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C boundary ids/counts and all16bit flags/list values; busy/group/unit/offset cases. MPYUW normalized for tested small operands; true apply children controlled, no nativeABI/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
