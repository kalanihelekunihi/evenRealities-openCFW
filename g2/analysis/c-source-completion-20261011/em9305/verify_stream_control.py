from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native 0x332a78..');body=s[a:s.index('/* Native30e510..',a)]
h='#include <stdint.h>\n#include <assert.h>\n#include <string.h>\n'+body+r'''
int main(void){uint8_t input[12];uint16_t output[8];for(unsigned n=0;n<256;n++){for(unsigned k=0;k<12;k++)input[k]=(uint8_t)(n+37*k);for(unsigned k=0;k<8;k++)output[k]=0xbeef;assert(opencfw_em9305_ll_stream_control_decode_332a78((uintptr_t)(output+1),(uintptr_t)input)==12);assert(output[0]==0xbeef&&output[7]==0xbeef);for(unsigned k=0;k<6;k++)assert(output[k+1]==(uint16_t)(input[2*k]+((uint32_t)input[2*k+1]<<8)));}return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':256,'native_range':'332a78..332aba','scope':'Actual selected C body, bounded native-reading data contract checks; not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('stream-control-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS256 controlled stream-control decode cases')
