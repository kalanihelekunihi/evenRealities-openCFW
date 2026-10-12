from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('extern uint32_t opencfw_em9305_radio_compose_323dc0'):s.index('extern uint32_t opencfw_em9305_radio_channels_317ac0')].replace('*(volatile uint32_t *)(uintptr_t)0x805a98u','fixture_global')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint32_t fixture_global,expected_flags,kind;static uintptr_t expected_record;
uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t record,uint32_t a,uint32_t flags,uint32_t c,uintptr_t event,uintptr_t length,uintptr_t output,uint32_t code,uint32_t count){assert(record==expected_record&&a==0&&flags==expected_flags&&c==0&&length==0x1234&&output==0x5678&&code==kind&&count==0xfedcba98);uint8_t *e=(uint8_t *)event;assert(e[0]==7&&e[1]==0&&e[2]==0&&e[3]==0&&e[4]==0);return 0x76543210;}
'''+b+r'''
int main(void){uint8_t record[1000]={0};unsigned cases=0;kind=7;expected_record=(uintptr_t)record;for(unsigned g=0;g<32;g++)for(unsigned field=0;field<256;field++)for(unsigned active=0;active<256;active++){fixture_global=0xffffffe0|g;record[716]=field;record[804]=active;expected_flags=(uint8_t)(((fixture_global>>1)&8)|(field&64)|(active<<2));assert(opencfw_em9305_radio_encode_324594((uintptr_t)record,0x5678,0x1234,0xfedcba98)==0x76543210);cases++;}kind=8;expected_record=0;for(unsigned flags=0;flags<65536;flags++){expected_flags=(uint8_t)flags;assert(opencfw_em9305_radio_encode_3245ec(flags,0x5678,0x1234,0xfedcba98)==0x76543210);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('compose-entry-host-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host actual C nine-argument forwarding, initialized five-byte local event, flag projection/byte narrowing and fullword count. Composition child controlled; native stack ABI and full child/runtime/hardware unqualified.'},indent=2)+'\n');print('PASS',n)
