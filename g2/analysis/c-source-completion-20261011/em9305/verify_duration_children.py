from pathlib import Path
import subprocess,tempfile,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31ac08'):s.index('extern uint32_t opencfw_em9305_radio_encode_3239d4')]
b=b.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','(uintptr_t)fixture_config').replace('uintptr_t row=0x805184u','uintptr_t row=(uintptr_t)(fixture_rows+8)')
b=re.sub(r'__asm__ volatile\("(mpywhl|mpyw|mpywhul|divu) %0,%1,%2":"=r"\((\w+)\):"r"\((\w+)\),"r"\((\w+)\)\);',lambda m:m[2]+'='+m[3]+('/' if m[1]=='divu' else '*')+m[4]+';',b)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t fixture_config[32],fixture_rows[12*255];
'''+b+r'''
static uint32_t piece(uint32_t p,uint32_t m,uint32_t n){return p==2?36+4*n:p==3?((27+8*n)*(m==1?2:8)+376):8*n+64;}
static uint32_t native_model(uint32_t phy,uint32_t request,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead){uint32_t r2=66,r13=66,r14=request,r1=request;if(!extended){r2=overhead;r13=overhead;if(!overhead){r2=10;r13=5;}}if(!request){r14=257-r2;r1=257-r13;}r2+=r14;uint32_t r3;if(r1>=size)r3=piece(phy,mode,(uint16_t)(r13+size));else{uint32_t r11=size/r14,r15=size-r11*r14,r8=(uint16_t)r15;if(!r8)r11--;uint32_t r0=piece(phy,mode,r2);r0+=spacing;r0+=300;r3=r0*r11;if(r8)r3+=piece(phy,mode,(uint16_t)(r15+r13));}return r3+timing;}
int main(void){unsigned cases=0;for(unsigned p=0;p<4;p++)for(unsigned mode=1;mode<=2;mode++)for(unsigned ext=0;ext<2;ext++)for(unsigned oh=0;oh<3;oh++)for(unsigned q=0;q<4;q++)for(unsigned size=0;size<=1024;size++){uint32_t requests[]={0,16,64,255},overheads[]={0,5,66};assert(opencfw_em9305_radio_duration_312be4(p,requests[q],123,7,size,ext,mode,overheads[oh])==native_model(p,requests[q],123,7,size,ext,mode,overheads[oh]));cases++;}
for(unsigned count=0;count<=255;count++)for(unsigned id=0;id<=256;id++){memset(fixture_rows,0,sizeof fixture_rows);fixture_config[13]=count;for(unsigned n=0;n<count;n++){fixture_rows[n*12+8]=(n%3)!=0;fixture_rows[n*12+9]=(uint8_t)n;}uint32_t expected=0;for(unsigned n=0;n<count;n++)if(n==id&&(n%3)!=0){expected=(uint32_t)(uintptr_t)(fixture_rows+n*12);break;}assert(opencfw_em9305_radio_record_ready_31ac08(id)==expected);cases++;}
printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('duration-children-host-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host controlled RAM and small nonzero-divisor word/DSP arithmetic; literal register-flow model. Native DIVU/MPYW/MPYWHL/MPYWHUL stay genuine assembly in target source. No full ISA overflow/divzero, runtime or hardware proof.'},indent=2)+'\n');print('PASS',n)
