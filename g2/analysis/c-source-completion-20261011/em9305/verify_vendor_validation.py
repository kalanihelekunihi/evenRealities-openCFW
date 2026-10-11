from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Authenticated nonexecutable default data334348'):s.index('/* Native331ec0..331efe')]
for addr,name in [('805b80','busy'),('805b82','valid_byte'),('805b18','handler_byte')]:body=body.replace('*(volatile uint8_t *)(uintptr_t)0x'+addr+'u',name)
body=body.replace('(void *)(uintptr_t)0x80527cu','(void *)product_data').replace('(void *)(uintptr_t)0x80525cu','(void *)product_key')
proof=json.loads(Path(__file__).with_name('vendor-default-data.json').read_text())
data=[bytes.fromhex(x['hex']) for x in proof['data']]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t busy,valid_byte,handler_byte,wake_byte,product_data[64],product_key[32],source_data[64];static unsigned copies,wakes,resident_calls,posts,rom_code;
static const uint8_t expected_key[32]={KEY};static const uint8_t expected_point[64]={POINT};
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(busy==1&&valid_byte==1);if(copies==0)assert(d==product_data&&n==64&&memcmp(s,expected_point,64)==0);else assert(copies==1&&d==product_key&&n==32&&memcmp(s,expected_key,32)==0);copies++;return memcpy(d,s,n);}
uintptr_t opencfw_em9305_wsf_wake_cell_313fc0(uintptr_t address){assert(address==0x805258&&copies==2);wakes++;wake_byte=1;return (uintptr_t)&wake_byte;}
uint32_t opencfw_em9305_rom_curve_validate_108260(uintptr_t point){resident_calls++;for(unsigned half=0;half<2;half++)for(unsigned group=0;group<8;group++)assert(memcmp((void*)(point+half*32+group*4),source_data+half*32+28-group*4,4)==0);handler_byte=77;return rom_code;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t event){assert(resident_calls==1&&handler==77&&event==4096);posts++;return 99;}
'''.replace('KEY',','.join(str(x) for x in data[0])).replace('POINT',','.join(str(x) for x in data[1]))+body+r'''
int main(void){unsigned cases=0;for(unsigned b=0;b<256;b++){busy=b;valid_byte=42;wake_byte=42;copies=wakes=0;memset(product_data,0xa5,64);memset(product_key,0xa5,32);assert(opencfw_em9305_ll_vendor_defaults_306d7c()==(b?12:0)&&copies==(b?0:2)&&wakes==!b&&busy==(b?b:1)&&valid_byte==(b?42:1)&&wake_byte==(b?42:2));cases++;}
for(unsigned pattern=0;pattern<256;pattern++){for(unsigned n=0;n<4;n++){for(unsigned r=0;r<3;r++){
 for(unsigned i=0;i<64;i++)source_data[i]=(uint8_t)(pattern+i*13);unsigned notify=n==3?0xffffffff:n==2?256:n;rom_code=r==2?0xffffffff:r;resident_calls=posts=0;handler_byte=42;assert(opencfw_em9305_ll_vendor_validate_32e328((uintptr_t)source_data,notify)==(rom_code==0)&&resident_calls==1&&posts==(rom_code!=0&&notify!=0));cases++;
}}}
for(unsigned shift=0;shift<=32;shift+=4){for(unsigned pattern=0;pattern<256;pattern++){
 _Alignas(4) uint8_t actual[64],expected[64];for(unsigned i=0;i<64;i++)actual[i]=(uint8_t)(pattern+i*17);memcpy(expected,actual,64);unsigned last=0;for(unsigned i=0;i<8;i++){unsigned part=16+28-i*4;uint8_t one=expected[part+1],two=expected[part+2],three=expected[part+3],zero=expected[part];last=one<<8;*(uint32_t*)(expected+shift+i*4)=zero+last+((unsigned)two<<16)+((unsigned)three<<24);}assert(opencfw_em9305_vendor_words_3333d0((uintptr_t)(actual+shift),(uintptr_t)(actual+16))==last&&memcmp(actual,expected,64)==0);cases++;
}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('vendor-validation-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Four actual C bodies including attributednonexecutabledefaultarrays. Allbusybytes,64Bpointpatternfixtures, notify0/1/256/ffffffff, residentreturn0/1/ffffffff with originalinput wordconversion verified, freshhandlerafterresidentcall, overlappingwordconverter fixtures andnativefinalR0return. ControlledresidentROM child; not ROMbody/native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
