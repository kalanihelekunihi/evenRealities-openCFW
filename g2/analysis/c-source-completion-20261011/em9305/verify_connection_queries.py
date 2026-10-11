from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();a=s.index('/* Native30c714..');body=s[a:s.index('/* Native306ff0..',a)]
body=body.replace('(uintptr_t)0x805ab6u','(uintptr_t)&limits[0]').replace('(uintptr_t)0x805ab8u','(uintptr_t)&limits[1]').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)config_data;')
h=r'''
#include <stdint.h>
#include <assert.h>
static uint16_t limits[2];static _Alignas(4) uint8_t config_data[40];
'''+body+r'''
int main(void){for(unsigned n=0;n<65536;n++){*(uint16_t*)(config_data+38)=n;uint16_t actual[4]={0x1234,0x5678,0x9abc,0xdef0},expected[4]={0x1234,0x5678,0x9abc,0xdef0};unsigned a=n&3,b=(n>>2)&3,c=(n>>4)&3,d=(n>>6)&3;uint32_t size=n>251?251:n;expected[a]=size;expected[b]=(size<<3)+112;uint32_t value=expected[a];expected[c]=value;value=expected[b];expected[d]=value;assert(opencfw_em9305_ll_connection_capabilities_30c78c((uintptr_t)(actual+a),(uintptr_t)(actual+b),(uintptr_t)(actual+c),(uintptr_t)(actual+d))==value);for(unsigned i=0;i<4;i++)assert(actual[i]==expected[i]);}
for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++){limits[0]=0x1234;limits[1]=0x9876;uint16_t actual[4]={0},expected[4]={0};expected[a]=limits[0];expected[b]=limits[1];assert(opencfw_em9305_ll_connection_limits_30c714((uintptr_t)(actual+a),(uintptr_t)(actual+b))==0x9876);for(unsigned i=0;i<4;i++)assert(actual[i]==expected[i]);}return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':65552,'native_ranges':['30c714..30c724','30c78c..30c7b0'],'scope':'Actual selected C bodies under normalized fixed RAM; full u16 input domain with destination alias contracts from native reading, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-queries-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS65552 controlled connection query cases')
