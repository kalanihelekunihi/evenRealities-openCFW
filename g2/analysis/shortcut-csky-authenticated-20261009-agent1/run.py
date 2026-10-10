from pathlib import Path
import hashlib,json,subprocess,os,sys
root=Path(__file__).resolve().parent
repo=root.parents[2]
campaign=repo/'g2/build/pseudocode-first/20260930T190500Z'
images={x['id']:x for x in map(json.loads,(campaign/'inventory/images.jsonl').open())}
tool=campaign/'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
launcher=repo/'g2/analysis/shortcut-ghidra-mcp-20261009-agent2/private-install/support/analyzeHeadless'
receipts=[]
jobs=[('binh_a_stage1',0x0fffffe8,0x10000acc,0x10000b08,'AuthenticatedStage1'),('binh_a_stage2_sram',0x10023400,0x10023500,0x10023530,'AuthenticatedStage2')]
if '--followup' in sys.argv:
    jobs=[('binh_a_stage2_sram',0x10023400,0x10023528,0x1002354c,'ClearBss'),('binh_a_stage2_sram',0x10023400,0x1002354c,0x100235f0,'SystemInit')]
for image,base,start,end,project in jobs:
    record=images[image]; source=repo/record['content_path']
    actual=hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual==record['content_sha256']
    mapping={'image':image,'source_path':record['content_path'],'source_sha256':actual,'source_size':source.stat().st_size,'file_to_conditional_runtime_addend':base,'analyzed_runtime_span':[start,end],'analyzed_child_span':[start-base,end-base],'component_span':record['mapping_model']['source']['component_span'],'route':record['mapping_model']['routes'][0],'qualification':'Stage1 header subtraction is intended coordinate hypothesis, resident delivery unverified. Stage2 normal route remains conditional.'}
    key=project if '--followup' in sys.argv else image
    (root/(key+'-mapping.json')).write_text(json.dumps(mapping,indent=2)+'\n')
    commands=[('objdump',[str(tool),'-D','-z','-b','binary','-m','csky',f'--adjust-vma={hex(base)}',f'--start-address={hex(start)}',f'--stop-address={hex(end)}',str(source)]),('ghidra',[str(launcher),str(root),project,'-import',str(source),'-loader','BinaryLoader','-loader-baseAddr',hex(base),'-processor','CSKY_V2:LE:32:default','-noanalysis','-scriptPath',str(root),'-postScript','ExportStartup.java',hex(start),hex(end)])]
    for kind,argv in commands:
        r=subprocess.run(argv,env=dict(os.environ,JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        out=root/(key+'-'+kind+'.txt');out.write_text(r.stdout)
        receipts.append({'argv':argv,'exit_code':r.returncode,'output':str(out.relative_to(repo)),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        print(image,kind,r.returncode)
(root/('followup-receipts.json' if '--followup' in sys.argv else 'receipts.json')).write_text(json.dumps(receipts,indent=2)+'\n')
