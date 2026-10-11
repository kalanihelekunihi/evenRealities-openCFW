from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30cd94/30b150'):s.index('/* Native30390c..303918')]
for a,n in [('805a74','flags[0]'),('805a73','flags[1]'),('805a71','flags[2]'),('805a72','flags[3]'),('805a9d','mode_byte')]:body=body.replace('*(volatile uint8_t *)(uintptr_t)0x'+a+'u',n)
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x80130cu','callback_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t flags[4],mode_byte;static uintptr_t callback_pointer;static unsigned gate_result,gates,resets;
static uint32_t gate(uintptr_t pointer){assert(pointer==(uintptr_t)&gate);gates++;return gate_result;}
uintptr_t opencfw_em9305_radio_reset_30390c(void){resets++;return 0x801610;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned pattern=0;pattern<16;pattern++)for(unsigned value=1;value<256;value++)for(unsigned installed=0;installed<2;installed++)for(gate_result=0;gate_result<2;gate_result++)for(unsigned mode=0;mode<4;mode++){for(unsigned i=0;i<4;i++)flags[i]=(pattern&(1u<<i))?value:0;callback_pointer=installed?(uintptr_t)&gate:0;mode_byte=99;gates=resets=0;unsigned busy=pattern||(installed&&gate_result);assert(opencfw_em9305_command_30cd94(mode)==(mode>=2?18:busy?12:0));assert(mode_byte==(mode>=2||busy?99:mode));assert(gates==(mode<2&&!pattern&&installed));for(unsigned m=0;m<2;m++){mode_byte=m;gates=resets=0;assert(opencfw_em9305_command_30b150()==(busy&&m?12:0));assert(resets==!(busy&&m)&&gates==(!pattern&&installed));n++;}}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('command-busy-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C ordered busy gates, allnonzero flagbyte values/presence patterns, callback presence/result, mode validation and reset branch. Normalized RAM/child; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
