from pathlib import Path
import hashlib, json, struct, subprocess, zipfile

R = Path(__file__).resolve().parents[3]
D = Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(n, v): (D/n).write_text(json.dumps(v, indent=2)+'\n')
target = json.loads((R/'g2/workflow/target.json').read_text())
identities=[]
for t in [target['bundle']]+target['components']:
    p=t.get('local_payload_path',t.get('verified_local_path'))
    b=(R/p).read_bytes()
    assert sha(b)==t['sha256'] and len(b)==t['size']
    identities.append({'path':p,'size':len(b),'sha256':sha(b)})
raw=(R/target['components'][-1]['local_payload_path']).read_bytes()
image=raw[32:]
def extent(a,b,label):
    v=image[a-0x438000:b-0x438000]
    return {'label':label,'start':hex(a),'end_exclusive':hex(b),'payload_offset':hex(a-0x438000+32),'size':len(v),'sha256':sha(v),'original_bytes_hex':v.hex()}
ranges=[extent(0x55ca94,0x55cc10,'configuration code extent; literal dependencies separate'),extent(0x55cc10,0x55cc18,'adjacent configuration literals'),extent(0x55cf38,0x55cf3c,'IOM base literal'),extent(0x55d248,0x55d278,'shared configuration literal pool subset')]
branches=[]
for rate,entry,load,store,lit,clk,word in [(100000,0x55cb88,0x55cb8c,0x55cb94,0x55d264,0x773b2301,0x3f070),(400000,0x55cb9a,0x55cb9e,0x55cba6,0x55d26c,0x1d0e2301,0x3f270),(1000000,0x55cbac,0x55cbb0,0x55cbb8,0x55d274,0x0b052301,0x23040)]:
    assert struct.unpack_from('<I',image,lit-0x438000)[0]==word
    assert struct.unpack_from('<I',image,lit-4-0x438000)[0]==clk
    # LDR.W r1,[PC,#imm12] uses aligned (instruction address+4).
    h1,h2=struct.unpack_from('<HH',image,load-0x438000)
    assert h1==0xf8df and h2>>12==1
    assert ((load+4)&~3)+(h2&0xfff)==lit
    assert image[store-0x438000:store-0x438000+4].hex()=='c2f8c012'
    branches.append({'rate_argument':rate,'branch_entry':hex(entry),'literal_load':hex(load),'store':hex(store),'literal_address':hex(lit),'old_word':hex(word),'new_default_word':hex(word|0x1000000),'stock_word':hex(word),'stock_STRDIS':(word>>24)&1,'CLKCFG':hex(clk),'receipt':extent(entry,entry+18,'branch instructions')})
assert struct.unpack_from('<I',image,0x55cf38-0x438000)[0]==0x40050000
zpath=Path.home()/'Downloads/AmbiqSuite_5.2.0.zip'
z=zipfile.ZipFile(zpath)
members=['AmbiqSuite_5.2.0/AmbiqSuite_5.2.0/mcu/apollo510/hal/mcu/am_hal_iom.c','AmbiqSuite_5.2.0/AmbiqSuite_5.2.0/CMSIS/AmbiqMicro/Include/apollo510.h']
baseline=R/'third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/mcu/am_hal_iom.c'
dump('stock-receipts.json',{'authenticated_inputs':identities,'image_sha256':sha(image),'address_mapping':'main payload file offset = virtual address - 0x438000 + 32','configuration_entry':'0x55ca94','code_end_exclusive':'0x55cc10','ranges':ranges,'branches':branches,'MMIO_address':'0x400502c0 + module*0x1000; module 0..7','result':'OLD for all three stock configuration writes','zip_sha256':sha(zpath.read_bytes()),'source_members':{n:sha(z.read(n)) for n in members},'baseline_sha256':sha(baseline.read_bytes())})
tool=subprocess.check_output(['arm-none-eabi-objdump','--version']).decode().splitlines()[0]
tmp=Path('/tmp/iom-strdis-main.bin');tmp.write_bytes(image)
dis=[]
for a,b in [(0x55ca94,0x55cc10),(0x55cf38,0x55cf3c),(0x55d248,0x55d278)]:
    dis.append(subprocess.check_output(['arm-none-eabi-objdump','-D','-b','binary','-marm','-Mforce-thumb','--adjust-vma=0x438000',f'--start-address={a}',f'--stop-address={b}',str(tmp)]).decode())
(D/'original-disassembly.txt').write_text(tool+'\nLiteral pool sections are data; objdump instructions there are not code claims.\n'+'\n'.join(dis))
# Read existing preservation policy without executing its mutation section.
ns={'__file__':str(R/'g2/analysis/audio-notification-block-insertion-2026-10-09/seal.py')}
policy=Path(ns['__file__']).read_text().split('baseline =',1)[0]
exec(policy,ns)
bad=[];count=0
for root in ['g2/analysis','g2/components']:
    for manifest in (R/root).rglob('DELIVERABLES.json'):
        if manifest.parent in ns['TARGETS'] or manifest.parent==D: continue
        data=json.loads(manifest.read_text())
        files=data.get('files',{}) if isinstance(data,dict) else {}
        if not isinstance(files,dict):continue
        for n,v in files.items():
            expected=v if isinstance(v,str) else v.get('sha256') if isinstance(v,dict) else None
            if not expected:continue
            p=R/n if n.startswith(('g2/','r1/','docs/','third-party/')) else manifest.parent/n
            count+=1
            if not p.is_file() or sha(p.read_bytes())!=expected:bad.append(str(p))
audit=json.loads((R/'g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/preservation-before.json').read_text())['audit']
auditbad=[n for n,v in audit.items() if sha((R/n).read_bytes())!=(v if isinstance(v,str) else v['sha256'])]
check=json.loads((R/'g2/analysis/rescan-2026-10-09T032723Z/snapshot.json').read_text())['checkpoints']
check={n:sha((R/v['path']).read_bytes())==v['sha256'] for n,v in check.items()}
before=json.loads((D/'input-identities.json').read_text())
dump('preservation.json',{'prior_sealed_entries':count,'seal_mismatches':bad,'audit_inputs':len(audit),'audit_mismatches':auditbad,'checkpoints':check,'index_sha256':sha((R/'.git/index').read_bytes()),'index_unchanged_since_start':sha((R/'.git/index').read_bytes())==before['index_sha256'],'registered_gitlinks':[l for l in subprocess.check_output(['git','ls-files','--stage'],cwd=R).decode().splitlines() if l.startswith('160000 ')]})
assert not bad and not auditbad and all(check.values())
print(json.dumps({'result':'OLD across all three stock branches','sealed_entries':count,'audit_inputs':len(audit),'checkpoints':check,'index_unchanged':sha((R/'.git/index').read_bytes())==before['index_sha256']},indent=2))
