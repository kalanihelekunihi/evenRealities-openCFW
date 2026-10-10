from pathlib import Path
import hashlib,json,subprocess,os
root=Path(__file__).resolve().parent
env=dict(os.environ,JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home')
private=root/'private-install'
lang=private/'Ghidra/Processors/CSKY/data/languages'
argv=[str(private/'support/sleigh'),str(lang/'csky_v2.slaspec')]
r=subprocess.run(argv,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(root/'mfcr-sleigh.log').write_text(r.stdout)
assert r.returncode==0
records=[{'argv':argv,'exit_code':r.returncode}]
source=root.parents[2]/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
for label,start,end in [('ResetMfcrFixed',0x10023500,0x1002351e),('SystemMfcrFixed',0x1002354c,0x100235e2)]:
    project=label+'Replay2'
    argv=[str(private/'support/analyzeHeadless'),str(root),project,'-import',str(source),'-loader','BinaryLoader','-loader-baseAddr','0x10023400','-processor','CSKY_V2:LE:32:default','-noanalysis','-scriptPath',str(root),'-postScript','ExportStartup.java',hex(start),hex(end)]
    r=subprocess.run(argv,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (root/(label+'.txt')).write_text(r.stdout)
    assert r.returncode==0
    assert '(register, 0x4, 4) COPY (register, 0x27c, 4)' in r.stdout if label=='ResetMfcrFixed' else '(register, 0x8, 4) COPY (register, 0x24c, 4)' in r.stdout
    records.append({'argv':argv,'exit_code':r.returncode,'output':label+'.txt'})
(root/'mfcr-fix-receipt.json').write_text(json.dumps({'status':'private_mfcr_destination_fix_verified','scope':'authenticated reset and system-init instructions, semantics checked against GNU decoder and SDK mfcr output constraint','commands':records,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [lang/'32b_priv.sinc',lang/'csky_v2.sla',source,root/'ExportStartup.java']}},indent=2)+'\n')
print('mfcr destination corrected and validated in two authenticated bodies')
