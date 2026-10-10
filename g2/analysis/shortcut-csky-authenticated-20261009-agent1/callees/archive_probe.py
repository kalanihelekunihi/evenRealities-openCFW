from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[3];binutils=repo/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
archive=repo/'third-party/upstream/nationalchip-lvp-kws/lib/libdriver_release_v1.0.6.a'; records=[]
def run(label,argv):
 r=subprocess.run(argv,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(root/(label+'.txt')).write_text(r.stdout);records.append({'argv':argv,'exit_code':r.returncode,'output':label+'.txt'});assert r.returncode==0;return r.stdout
run('driver-symbols',[str(binutils/'csky-elfabiv2-nm'),'-A',str(archive)])
run('extract-provider-objects',[str(binutils/'csky-elfabiv2-ar'),'x',str(archive),'pmu_ctrl.o','misc.o'])
for name in ['gx_pmu_get_start_mode','gx_pmu_get_wakeup_source','gx_analog_config_update_enable']:
 obj=root/('misc.o' if name.startswith('gx_analog') else 'pmu_ctrl.o')
 run(name+'-section-disassembly',[str(binutils/'csky-elfabiv2-objdump'),'-dr','-j','.text.'+name,str(obj)])
 out=root/(name+'.bin');run(name+'-section',[str(binutils/'csky-elfabiv2-objcopy'),'-O','binary','-j','.text.'+name,str(obj),str(out)])
image=repo/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
stock=image.read_bytes()[0x1584:0x15a2];candidate=(root/'gx_pmu_get_start_mode.bin').read_bytes()
match=len(stock)==len(candidate) and stock[:2]==candidate[:2] and stock[6:]==candidate[6:]
source_bytes=image.read_bytes(); wake=(root/'gx_pmu_get_wakeup_source.bin').read_bytes()
wake_match=source_bytes[0x1540:0x1540+len(wake)]==wake
inventory={x['id']:x for x in map(json.loads,(repo/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').open())};xip=inventory['binh_a_stage2_xip'];xip_path=repo/xip['content_path'];assert hashlib.sha256(xip_path.read_bytes()).hexdigest()==xip['content_sha256'];analog=(root/'gx_analog_config_update_enable.bin').read_bytes();analog_offset=0x10203c74-0x10203004
analog_match=xip_path.read_bytes()[analog_offset:analog_offset+len(analog)]==analog
(root/'archive-receipt.json').write_text(json.dumps({'archive_path':str(archive.relative_to(repo)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'commands':records,'start_mode_body_equal_except_call_relocation':match,'stock_body_length':len(stock),'candidate_length':len(candidate),'excluded_relocation_span':[2,6],'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'wakeup_source_exact_match':wake_match,'wakeup_source_runtime':0x10024940,'wakeup_source_section_bytes':len(wake),'analog_update_exact_match':analog_match,'analog_runtime':0x10203c74,'analog_xip_child_offset':analog_offset,'analog_section_bytes':len(analog),'xip_sha256':xip['content_sha256']},indent=2)+'\n')
print('start_mode match except relocation:',match,len(stock),len(candidate))
