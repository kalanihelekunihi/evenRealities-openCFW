from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30ca68..30cac4'):s.index('/* Native303b40..303b7c')].replace('*(volatile uint8_t *)(uintptr_t)0x805a9du','mode_byte')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t input[6],mode_byte;static uint32_t kind,busy,found,gates,packs,sets;
static uint32_t opencfw_em9305_command_busy_native(void){gates++;return busy;}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t p){assert(p==(uintptr_t)input&&gates==1);packs++;return 0x123456789abcdef0ULL;}
uint32_t opencfw_em9305_radio_address_update_303b40(uint32_t k,uint32_t l,uint32_t h){assert(k==kind&&l==0x9abcdef0&&h==0x12345678&&packs==1);sets++;return found;}
'''+body+r'''
int main(void){unsigned n=0;for(kind=0;kind<256;kind++)for(busy=0;busy<2;busy++)for(unsigned m=0;m<2;m++)for(found=0;found<2;found++){mode_byte=m;gates=packs=sets=0;unsigned valid=kind<=1;unsigned blocked=valid&&busy&&m;unsigned status=!valid?18:blocked?12:found?0:18;assert(opencfw_em9305_command_30ca68(kind,(uintptr_t)input)==status);assert(gates==valid&&packs==(valid&&!blocked)&&sets==packs);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('address-update-command-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C allkindbytevalues, busy/mode gate, lookup0/nonzero and ordered packedaddress args. Normalized real children/RAM; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
