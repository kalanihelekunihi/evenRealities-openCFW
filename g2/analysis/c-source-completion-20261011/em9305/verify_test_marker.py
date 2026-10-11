from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30b1ac tail'):s.index('extern uint32_t opencfw_em9305_ll_test_submit_31bb20')]
h='#include <stdint.h>\n#include <assert.h>\n'+body+'\nint main(void){uint8_t request[4];for(unsigned i=0;i<256;i++){request[1]=i;assert(opencfw_em9305_ll_test_30b1ac((uintptr_t)request)==((i==255||i<=1)?0:18));}return 0;}\n'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);subprocess.run([str(d/'t')],check=True)
Path(__file__).with_name('test-marker-receipt.json').write_text(json.dumps({'cases_passed':256,'scope':'Actual C body; byte-wrap and native unsigned LO branch contract from 306b70..306b7c. Not native runtime execution.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS256')
