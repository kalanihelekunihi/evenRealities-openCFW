# SPDX-License-Identifier: MIT
"""Feed decoded KWS runner task words into the reconstructed SNPU queue."""
import json,subprocess
from verify_gx8002_kws_run import verify as qualify,expected,ROOT,sha,decode,Elf32
from execute_gx8002_kws_run import execute
from verify_gx8002_snpu_run_task import execute as submit,ADDRESS
from model_gx8002_snpu_run_task import Case,Model,expected as queue_expected

def verify():
    evidence=qualify()
    path=ROOT/'build/gx8002-source-candidate/snpu-run-task/snpu-run-task.elf'
    elf=Elf32(path.read_bytes(),'submission')
    report=json.loads((ROOT/'docs/research/gx8002-snpu-run-task-verification.json').read_text())
    row=report['functions'][0]
    section=next(s for s in elf.sections if s['name']==row['section_name'])
    assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    runner=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text())
    cases=0;accepted=0;rejected=0
    for start,end in ((0,0),(0,9),(9,8),(9,9),(5,2)):
      for state in (0,1,2):
       for registers in (0,0xa0c00000):
        for seed in (0,0xffffffff):
         outcomes=[]
         def enqueue(task,callback,private,words):
            case=Case(start=start,end=end,state=state,task=task,callback=callback,private=private,registers=registers,seed=seed)
            actual_model=Model(case);oracle_model=Model(case)
            task_words={task+4*i:words[task+4*i] for i in range(8)}
            actual_model.words.update(task_words);oracle_model.words.update(task_words)
            actual=submit(code,ADDRESS,0,case,model=actual_model)
            assert actual==queue_expected(case,model=oracle_model)
            outcomes.append(actual[2])
            return actual[2]
         args=(0x20030000,2,1,0x20058000,0x20059000,520,seed)
         assert execute(runner,0x100260e4,evidence['candidate']['bindings'],*args,submit_hook=enqueue)==expected(*args)
         assert len(outcomes)==1
         if outcomes[0]==0:accepted+=1
         else:assert outcomes[0]==0xffffffff;rejected+=1
         cases+=1
    assert accepted and rejected
    return {'evidence':evidence,'submission_cases':cases,'accepted':accepted,'rejected':rejected,'submission_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual decoded runner stack task words feed decoded submission; queue writes and ordered calls compared with independent model. Runner returns zero even when submission rejects, matching stock behavior. Resume and hardware submit helpers remain modeled; no physical execution or full firmware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-submission.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ('submission_cases','accepted','rejected')})
