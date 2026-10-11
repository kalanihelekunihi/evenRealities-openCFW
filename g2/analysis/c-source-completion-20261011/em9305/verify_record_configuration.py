from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native32c3bc..32c4fc'):s.index('/* Native31737c..3173ac')].replace('__asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(a),"r"(b));','result=a*b;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t record[512],input[40];static unsigned timing,randoms,seeds,mutate;
static const uint8_t opencfw_em9305_radio_phy_values_334488[7]={2,1,3,1,1,1,4};
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t v){assert(v==2);return 2;}
uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t p,uint32_t n){assert((p==(uintptr_t)(record+485)&&n==8)||(p==(uintptr_t)(record+493)&&n==16));randoms++;return 0;}
void opencfw_em9305_radio_encrypt_seed_317334(uintptr_t a,uintptr_t b,uintptr_t c){assert(a==(uintptr_t)(record+493)&&b==(uintptr_t)(input+17)&&c==(uintptr_t)(record+92)&&randoms==2);seeds++;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t length,uint32_t size){unsigned period=*(uint32_t *)(input+4);unsigned expected=(period%1250||input[15]==1)?(length>210?251:length+40):(length<251?length:251);assert(length==*(uint16_t *)(input+8)&&size==expected);if(mutate)record[4]=17;return timing;}
uint32_t opencfw_em9305_radio_phy_duration_31737c(uint32_t phy,uint32_t size,uint32_t secure){assert(phy==2&&size==record[4]&&secure==(input[16]!=0));return 100;}
'''+b+r'''
int main(void){unsigned n=0;unsigned periods[]={0,2500,2501},lengths[]={200,211,300};
for(unsigned mode=0;mode<2;mode++)for(unsigned secure=0;secure<2;secure++)for(unsigned kind=0;kind<2;kind++)for(unsigned p=0;p<3;p++)for(unsigned l=0;l<3;l++)for(unsigned t=0;t<2;t++)for(mutate=0;mutate<2;mutate++){
 memset(record,0,512);memset(input,0,40);input[2]=2;*(uint32_t *)(input+4)=periods[p];*(uint16_t *)(input+8)=lengths[l];input[12]=1;input[13]=2;input[14]=mode;input[15]=kind;input[16]=secure;timing=t?3:0;randoms=seeds=0;
 opencfw_em9305_radio_record_configure_32c3bc((uintptr_t)record,(uintptr_t)input);unsigned groups=timing*2,a=mode?250:250*groups,b=mode?500:250;unsigned span=a+100+b*(groups-1);unsigned total=5000;if(timing&&periods[p])total=(periods[p]-periods[p]%1250)+((kind||periods[p]%1250)?periods[p]+span:span-periods[p]);
 assert(record[3]==1&&record[31]==mode&&record[30]==(kind||periods[p]%1250)&&record[292]==2&&record[484]==secure&&randoms==2*secure&&seeds==secure);assert(*(uint16_t *)(record+6)==lengths[l]&&record[24]==timing&&record[25]==groups&&record[27]==2&&record[26]==0&&*(uint16_t *)(record+28)==511);assert(*(uint32_t *)(record+12)==a&&*(uint32_t *)(record+48)==b&&*(uint32_t *)(record+40)==span&&*(uint32_t *)(record+44)==total);n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-configuration-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C mode/encryption/kind/period/length/timing/freshsize-childmutation cuts, write layout and branch arithmetic. MPYWHL normalized as fixture scalar multiplication for small operands, real children normalized; nativeDSP/ISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
