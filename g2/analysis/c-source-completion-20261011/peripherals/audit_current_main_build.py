"""Audit a terminal Main receipt against current source and build artifacts."""
from pathlib import Path
import json,hashlib,sys
folder=Path(sys.argv[1]);receipt=json.loads((folder/'receipt.json').read_text());image=receipt['images']['apollo_main'];snap=[]
def walk(value):
    if isinstance(value,dict):
        if 'compile_source_snapshot' in value:snap.append(value['compile_source_snapshot'])
        for key,item in value.items():
            if key!='compile_source_snapshot':walk(item)
    elif isinstance(value,list):
        for item in value:walk(item)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
walk(receipt)
assert image['candidate_compilation_passed'] and image['archive_inputs_present']
assert all(command['returncode']==0 for command in image['build_commands'])
link=image['relocatable_link'];assert link['returncode']==0 and not link['duplicate_strong_symbols']
for source in snap:
    assert source['stable_during_command'] and source['sha256_before']==source['sha256_after']==sha(source['path']),source['path']
for artifact in image['artifacts']:
    assert artifact['sha256']==sha(artifact['path']),artifact['path']
assert link['output_sha256']==sha(link['output'])
assert receipt['builder_sha256']==sha('g2/firmware_c/build.py')
audit={'status':'PASS_STABLE_CURRENT_SOURCE_AND_RELOCATABLE_LINK','snapshots':len(snap),'definitions':len(link['defined_symbols']),'imports':len(link['unresolved_symbols']),'duplicate_strong_symbols':0,'artifact_hashes_checked':len(image['artifacts'])+1,'builder_hash_checked':True,'limits':['Full coverage/layout/byte equality/hardware unproven.']}
(folder/'root-source-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
