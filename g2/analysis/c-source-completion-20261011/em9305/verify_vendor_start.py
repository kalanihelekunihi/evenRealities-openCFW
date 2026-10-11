from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native313fc0..'):s.index('/* Authenticated nonexecutable default data334348')]
for addr,name in [('805b80','busy'),('805b83','host_mode'),('805b82','valid_byte')]:body=body.replace('*(volatile uint8_t *)(uintptr_t)0x'+addr+'u',name)
body=body.replace('0x80606du','((uintptr_t)&wake_byte)').replace('(void *)(uintptr_t)0x80527cu','(void *)product_data').replace('(void *)(uintptr_t)0x80525cu','(void *)product_key').replace('(const void *)(uintptr_t)0x805b60u','(const void *)key_data')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t busy,host_mode,valid_byte,wake_byte,first[32],second[32],key_data[32],product_data[64],product_key[32];static unsigned valid,mutate,validators,copies,defaults,original_mode;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){copies++;return memcpy(d,s,n);}
uint32_t opencfw_em9305_ll_vendor_validate_32e328(uintptr_t data,uint32_t zero){assert(zero==(original_mode==0));assert(memcmp((void*)data,first,32)==0&&memcmp((void*)(data+32),second,32)==0);validators++;if(mutate)host_mode=255;return valid;}
uint32_t opencfw_em9305_ll_vendor_defaults_306d7c(void){defaults++;return 0xcafe;}
'''+body+r'''
int main(void){unsigned cases=0;unsigned values[]={0,1,256,0xffffffff};for(unsigned b=0;b<256;b++){for(original_mode=0;original_mode<3;original_mode++){for(unsigned vi=0;vi<4;vi++){valid=values[vi];for(mutate=0;mutate<2;mutate++){for(unsigned kind=0;kind<3;kind++){
 for(unsigned i=0;i<32;i++){first[i]=i*13;second[i]=i*17;key_data[i]=i*19;}memset(product_data,0xa5,64);memset(product_key,0xa5,32);busy=b;host_mode=original_mode;valid_byte=42;wake_byte=42;validators=copies=defaults=0;
 unsigned special=kind==2,accept=!special&&b==0&&valid!=0,expected=special?0xcafe:b?12:valid?0:original_mode?18:0;
 unsigned actual=kind==0?opencfw_em9305_ll_vendor_apply_30baa0((uintptr_t)first,(uintptr_t)second):opencfw_em9305_ll_vendor_apply_30bad4((uintptr_t)first,(uintptr_t)second,special?1:256);
 assert(actual==expected&&defaults==special&&validators==(!special&&b==0)&&copies==(special?0:3+(accept?2:0)));assert(valid_byte==(!special&&b==0?(uint8_t)valid:42)&&busy==(accept?1:b)&&wake_byte==(accept?2:42));if(accept){assert(memcmp(product_data,first,32)==0&&memcmp(product_data+32,second,32)==0&&memcmp(product_key,key_data,32)==0);}cases++;
}}}}}for(unsigned b=0;b<256;b++){busy=b;wake_byte=42;assert(opencfw_em9305_ll_vendor_query_30bb10()==(b?12:0)&&busy==(b?b:1)&&wake_byte==(b?42:1));cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('vendor-start-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Five actual C bodies normalized product/wake cells, controlled validator/defaults and copy. Allbusybytes, modes0/1/2, fullword validator0/1/256/ffffffff, mode mutation, native96B scratch layout/copy counts, count1/default versus fullword256/application, queued wake1/2 and querybusy gates. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
