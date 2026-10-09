from pathlib import Path
import hashlib,json,subprocess
O=Path(__file__).resolve().parent;R=O.parents[2];C=R/'g2/build/pseudocode-first/20260930T190500Z';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=C/'reviews/codec-canonical-images-003/images'; tool=C/'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
inputs=[tool,B/'binh_a_stage2_xip.bin',B/'binh_a_stage2_sram.bin']
assert sha(inputs[1])=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584';assert sha(inputs[2])=='53860d6974097ad494c6697df52f95b796360131fab63cd8bfd7efc9c5596de8'
checks=[]
for name,img,base,start,end in [('put',inputs[2],0x10023400,0x100261b8,0x10026212),('get',inputs[1],0x10203004,0x10206fb0,0x10206ffa)]:
 argv=[str(tool),'-D','-b','binary','-m','csky','-EL',f'--adjust-vma={hex(base)}',f'--start-address={hex(start)}',f'--stop-address={hex(end)}',str(img)]
 t=subprocess.run(argv,capture_output=True,text=True,check=True).stdout
 assert f'{start:x}:' in t and 'divs' in t
 (O/(name+'-instructions.txt')).write_text(t)
 checks.append({'name':name,'range':[hex(start),hex(end)],'sha256':hashlib.sha256(img.read_bytes()[start-base:end-base]).hexdigest(),'command':argv})
k=R/'third-party/upstream/nationalchip-lvp-kws';a=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/nationalchip-lvp-aiot'
for root in [k,a]:
 for f in ['lvp/common/lvp_queue.c','lvp/common/lvp_queue.h','include/lvp_attr.h','arch/soc/grus/link.ld']:inputs.append(root/f)
kt=(k/'lvp/common/lvp_queue.c').read_text();at=(a/'lvp/common/lvp_queue.c').read_text()
assert '\nint LvpQueueGet(' in kt and 'DRAM0_STAGE2_SRAM_ATTR int LvpQueueGet(' in at
for root in [k,a]:
 assert 'section(".sram_text")' in (root/'include/lvp_attr.h').read_text()
 assert '*(.sram_text*)' in (root/'arch/soc/grus/link.ld').read_text()
(O/'results.json').write_text(json.dumps({'status':'PASS','inputs':{str(p.relative_to(R)):sha(p) for p in inputs},'slices':checks,'original_instruction_execution':False,'source_rebuild':False,'inference':'Stock SRAM Put / XIP Get agrees with unchanged KWS source under default-text-in-flash profile. Acquired unchanged AIoT Get explicitly selects SRAM under its supplied attribute/linker contract. Modified source/attributes/linker remain alternatives; no exact revision attribution.'},indent=2)+'\n')
print('PASS: two byte-bound slices and both source section contracts')
