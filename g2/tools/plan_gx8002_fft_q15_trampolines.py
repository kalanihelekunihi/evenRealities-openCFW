# SPDX-License-Identifier: MIT
"""Search source-function placement with alternative preserved-entry stubs."""
import itertools,json
from build_gx8002_backup_cfft import ROOT,sha

def plan(clock_tail=False):
    path=ROOT/'docs/research/gx8002-fft-q15-lto-materialized.json';report=json.loads(path.read_text())
    tail_evidence=None
    if clock_tail:
        tail_path=ROOT/'docs/research/gx8002-backup-replacement-tails.json'
        census=json.loads(tail_path.read_text())
        build_path=ROOT/'build/gx8002-source-candidate/build-report.json'
        assert sha(build_path.read_bytes())==census['source_build_report_sha256']
        tail_evidence=next(t for t in census['tails'] if t['function']=='clock_lookup')
        assert tail_evidence['bytes']==32 and not tail_evidence['reclaim_admitted']
    sections=[s.copy() for s in report['sections'] if s['flags']&4]
    entries={'rfft':0x478a4,'shift_q15':0x47a00,'maxabs_q15':0x47a74,'copy_q15':0x47ac0,'fill_q15':0x47aec}
    attempts=[];solution=None
    for count in range(1,6):
      for names in itertools.combinations(entries,count):
        if 'copy_q15' not in names:continue
        items=sections[:];reserved=[]
        for name,offset in entries.items():
            section=next(s for s in sections if s['section']=='.text.open_cfw_gx8002_backup_'+name)
            size=4 if name in names else section['size']
            if name not in names:items.remove(section)
            reserved.append({'entry':name,'section':section['section'],'offset':offset,'size':size,'branch':name in names})
        ordered=sorted(reserved,key=lambda r:r['offset']);ranges=[];cursor=0x478a4
        if any(a['offset']+a['size']>b['offset'] for a,b in zip(ordered,ordered[1:])):continue
        for row in ordered:
            if cursor<row['offset']:ranges.append((cursor,row['offset']))
            cursor=row['offset']+row['size']
        ranges.extend([(cursor,0x4818a),(0x4cd34,0x4cf14)])
        if tail_evidence:ranges.append(tuple(tail_evidence['tail']))
        positions=[(a+3)&~3 for a,b in ranges];bins=[[] for _ in ranges];items.sort(key=lambda s:-s['size']);failed=set()
        def search(index):
            if index==len(items):return True
            key=(index,tuple(positions),tuple(any(x['size']%4==2 for x in group) for group in bins))
            if key in failed:return False
            item=items[index]
            for n,(lo,hi) in enumerate(ranges):
                old=positions[n];start=old;assert item['align']==4
                rounded=(item['size']+3)&~3
                refund=2 if item['size']%4==2 or any(x['size']%4==2 for x in bins[n]) else 0
                if start+rounded-refund>hi:continue
                positions[n]=start+rounded;bins[n].append({'section':item['section'],'offset':start,'size':item['size']})
                if search(index+1):return True
                bins[n].pop();positions[n]=old
            failed.add(key);return False
        fits=search(0);attempts.append({'branch_entries':names,'fits':fits,'rejected_states':len(failed)})
        if fits:
            for (lo,hi),group in zip(ranges,bins):
                tail=next((x for x in group if x['size']%4==2),None)
                if tail:group.remove(tail);group.append(tail)
                cursor=(lo+3)&~3
                for item in group:
                    item['offset']=cursor;assert cursor+item['size']<=hi
                    cursor=(cursor+item['size']+3)&~3
            solution={'reserved':reserved,'ranges':ranges,'placements':bins};break
      if solution:break
    result={'clock_tail_candidate':tail_evidence,'materialized_report_sha256':sha(path.read_bytes()),'attempts':attempts,'solution':solution,'source_admitted':False,'limits':['Any clock tail is an unadmitted candidate only; no reuse qualification implied. Four-byte branch reservations; whole compiler sections and original alignment retained. No code emitted or branch reachability/loader behavior qualified.']}
    (ROOT/('docs/research/gx8002-fft-q15-clock-tail-plan.json' if clock_tail else 'docs/research/gx8002-fft-q15-trampoline-plan.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=plan();print([(a['branch_entries'],a['fits']) for a in r['attempts']])
