from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
b=s[s.index('/* Native303788..303844'):s.index('/* Native331f5c..332036')]
b=b.replace('*(volatile uint8_t *)(uintptr_t)0x801610u','count_byte').replace('*(volatile uint8_t *)(uintptr_t)0x801611u','capacity_byte').replace('*(volatile uint32_t *)(uintptr_t)0x805c00u','base_pointer').replace('__asm__ volatile("mpyuw %0,%1,72":"=r"(offset):"r"(count));','offset=count*72u;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(8) uint8_t rows[72*256],existing[72],first[16],second[16];
static uint8_t count_byte,capacity_byte;static uintptr_t base_pointer;static unsigned found,projects;
uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t k,uint32_t l,uint32_t h){assert(k==1&&l==0x12345678&&h==0xabcd);return found?(uintptr_t)existing:0;}
void *opencfw_em9305_memcpy(void *d,const void *s,unsigned n){return memcpy(d,s,n);}
void *opencfw_em9305_memset(void *d,unsigned v,unsigned n){return memset(d,v,n);}
uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t p){uint8_t *r=(uint8_t *)p-16;assert(r[65]==0&&r[66]==0&&r[67]==0);for(unsigned i=40;i<64;i++)assert(r[i]==0);projects++;return 0xabcdef0198765432ULL;}
'''+b+r'''
int main(void){unsigned n=0;for(unsigned c=0;c<4;c++)for(found=0;found<2;found++)for(unsigned null=0;null<2;null++)for(unsigned a=0;a<17;a++)for(unsigned z=0;z<17;z++){
 memset(rows,0xa5,sizeof rows);memset(existing,0xa5,sizeof existing);memset(first,0,16);memset(second,0,16);if(a)first[a-1]=7;if(z)second[z-1]=9;
 count_byte=c;capacity_byte=3;base_pointer=null?0:(uintptr_t)rows;projects=0;
 unsigned success=found||(!null&&c<3);unsigned result=opencfw_em9305_radio_identity_add_303788(1,0x12345678,0xabcd,(uintptr_t)first,(uintptr_t)second);assert(result==success);assert(count_byte==c+(!found&&c<3));assert(projects==(success&&z!=0));
 if(success){uint8_t *r=found?existing:rows+c*72;assert(!memcmp(r,first,16)&&!memcmp(r+16,second,16));assert(*(uint32_t *)(r+32)==0x12345678&&*(uint32_t *)(r+36)==0x1abcd);assert(r[64]==(a==0)&&r[65]==(z==0)&&r[66]==0&&r[67]==0);for(unsigned i=40;i<64;i++){uint8_t expected=0;if(z&&i>=48&&i<56){uint64_t v=0xabcdef0198765432ULL;expected=(uint8_t)(v>>((i-48)*8));}assert(r[i]==expected);}assert(r[68]==0xa5&&r[39]==0);}
 else{for(unsigned i=0;i<sizeof rows;i++)assert(rows[i]==0xa5);}n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('identity-insertion-receipt.json').write_text(json.dumps({'cases_passed':n,'source_body_sha256':hashlib.sha256(b.encode()).hexdigest(),'scope':'Actual selected C record updates, capacity/null-base/count ordering, zero key scans and projection paths. Fixed RAM, child calls and MPYUW normalized; no native ISA or hardware execution.'},indent=2)+'\n');print('PASS',n)
