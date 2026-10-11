from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native3183d4..3183ec'):s.index('/* Native32c3bc..32c4fc')]
binary=root/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin';d=binary.read_bytes();assert hashlib.sha256(d).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03';native=list(d[0x334488-0x302400:0x33448f-0x302400])
h='#include <stdint.h>\n#include <assert.h>\n#include <stdio.h>\n'+b+r'''
int main(void){unsigned n=0;for(unsigned high=0;high<4;high++)for(unsigned low=0;low<65536;low++){uint32_t value=(high==0?0:high==1?0x80000000:high==2?0xffff0000:0x12340000)|low;unsigned expected=(value&2)?2:(value&1)?1:(value&4);assert(opencfw_em9305_radio_phy_project_3183d4(value)==expected);n++;}
const uint8_t expected[7]={'''+','.join(map(str,native))+r'''};for(unsigned i=0;i<7;i++)assert(opencfw_em9305_radio_phy_values_334488[i]==expected[i]);printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('phy-projection-receipt.json').write_text(json.dumps({'cases_passed':n,'data_bytes_matched':7,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'scope':'Actual C all16lowbits/four highword fixtures and exact authenticated bounded data. No native ISA execution/placement/hardware proof.'},indent=2)+'\n');print('PASS',n,'DATA',len(native))
