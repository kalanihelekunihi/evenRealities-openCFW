from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native306a90..306a9c'):s.index('/* Native30ddd4..30de38')].replace('*(volatile uint8_t *)(uintptr_t)0x805400u','mode_byte').replace('*(volatile uint32_t *)(uintptr_t)0x801300u','callback_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t mode_byte;static uintptr_t callback_pointer;static uint32_t gate_value,gate_calls,callback_calls,selector,mode;
uint32_t opencfw_em9305_ll_connection_gate_30e524(void){gate_calls++;return gate_value;}
static uint32_t callback(uint32_t s,uint32_t m){assert(s==selector&&m==mode&&gate_calls==1);callback_calls++;return 0x12345678;}
'''+body+r'''
int main(void){unsigned n=0;for(selector=0;selector<256;selector++)for(mode=0;mode<256;mode++)for(unsigned g=0;g<3;g++)for(unsigned present=0;present<2;present++){gate_value=g==2?0x100:g;callback_pointer=present?(uintptr_t)&callback:0;mode_byte=99;gate_calls=callback_calls=0;unsigned expected=mode>=4?18:gate_value?0:present?0x12345678:18;assert(opencfw_em9305_command_30d45c(selector,mode)==expected);assert(gate_calls==(mode<4)&&callback_calls==(mode<4&&!gate_value&&present));assert(mode_byte==(mode<4&&gate_value?mode:99));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('mode-provider-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Two actual C bodies, allselector/modebytes, fullwordgate outcomes, callbackpresence/fullreturn and writegates. Normalized RAM/children; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
