#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4]
s=(R/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
start=s.index('uint32_t opencfw_em9305_init_slave_phy_predicate_329534(uintptr_t record)');end=s.index('\nuint32_t opencfw_em9305_init_lower_307d64',start);body=s[start:end]
# Compile the actual selected C body, without a copied implementation.
harness='#include <stdint.h>\n'+body+"\nint main(void){uint8_t record[636]={0};for(unsigned a=0;a<256;a++)for(unsigned b=0;b<256;b++){record[635]=a;record[625]=b;uint32_t native=(a==21 && (((uint32_t)b-1u)<2u));if(opencfw_em9305_init_slave_phy_predicate_329534((uintptr_t)record)!=native)return 1;}return 0;}\n"
with tempfile.TemporaryDirectory() as d:
 c=Path(d)/'check.c';exe=Path(d)/'check';c.write_text(harness)
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
r={'status':'PASS_SELECTED_C_PREDICATE_ALL_BYTE_PAIRS','input_pairs':65536,'callback_cell':'805688','native_writer':'30a37c','native_target':'329534','body_sha256':hashlib.sha256(body.encode()).hexdigest(),'limits':['Native initialization path reachability, computed overwrites, target ABI and hardware execution remain separate gates.']}
(P/'callback-predicate-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
