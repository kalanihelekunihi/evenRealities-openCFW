# SPDX-License-Identifier: MIT
"""Native host contract check; not a decoded stock equivalence proof."""
import json,subprocess
from build_gx8002_dma_descriptors import build,ROOT,sha

def verify():
    candidate=build();out=ROOT/'build/gx8002-dma-descriptors';test=ROOT/'tests/gx8002_dma_descriptors_host_check.c';source=ROOT/'components/shared/gx8002/runtime_gx8002_dma_descriptors.c'
    binary=out/'host-check'
    subprocess.run(['clang','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(test),str(source),'-o',str(binary)],check=True)
    result=subprocess.check_output([str(binary)],text=True).strip()
    if result!='Descriptor host cases: 15552':raise ValueError(result)
    return {'candidate':candidate,'host_cases':15552,'sanitizers':['address','undefined'],'test_sha256':sha(test.read_bytes()),'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Host contract uses modeled address translation; target instruction equivalence remains pending. Separate pattern/output arrays, count 0..17; negative lengths are arithmetic probes.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-descriptors-host.json').write_text(json.dumps(report,indent=2)+'\n');print('Descriptor host cases:',report['host_cases'])
