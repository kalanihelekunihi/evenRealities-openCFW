from pathlib import Path
import json,hashlib,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True
groups=[('flash','flash216-data',[('process',0x8bf4,128,True),('valid',0x8c74,52,True),('row',0x8ca8,28,True),('backup',0x8cc4,60,False),('config',0x8d00,32,False),('restore',0x8d20,48,False),('write_row',0x8d50,216,False),('switch',0xb51c,80,True)]),('ilo','ilo-data',[('start',0x9d90,76,False),('stop',0x9ddc,60,False),('compensate',0x9e18,284,False),('division',0xa6c0,276,True),('zero',0xa9a8,4,True)]),('pm','pm-data',[('execute',0xa444,228,False)])]
code_map={'ProcessStatusCode':0x8bf4,'Cy_Flash_ValidAddr':0x8c74,'Cy_Flash_GetRowNum':0x8ca8,'Cy_Flash_ClockBackup':0x8cc4,'Cy_Flash_ClockConfig':0x8d00,'Cy_Flash_ClockRestore':0x8d20,'Cy_Flash_WriteRow':0x8d50,'Cy_SysLib_EnterCriticalSection':0x4492,'Cy_SysLib_ExitCriticalSection':0x449a,'memcpy':0xaa2c,'__aeabi_uidiv':0xa6c0,'Cy_SysClk_IloStartMeasurement':0x9d90,'Cy_SysClk_IloStopMeasurement':0x9ddc,'Cy_SysClk_IloCompensate':0x9e18,'Cy_SysPm_ExecuteCallback':0xa444}
data_map={'.rodata.ProcessStatusCode':0xb51c,'.bss.cySysFlashBackup':0x20000f04,'.bss.preventIloMeasurment':0x20000f1d,'.bss.iloMeasurment':0x20000f1e,'.bss.compRunStat.0':0x20000f1c,'SystemCoreClock':0x20000878,'.bss.pmCallbackRoot':0x20000f34,'.bss.lastExecutedCallback.0':0x20000f24,'.bss.failedCallback':0x20000f28};runs=[]
for label,input_label,sections in groups:
 idir=O/'outputs'/input_label;out=O/'linked'/label;out.mkdir(parents=True,exist_ok=True);evidence=[]
 with (idir/'public.o').open('rb') as f:
  e=ELFFile(f)
  for q in e.iter_sections():
   if q['sh_type']!='SHT_REL':continue
   s=e.get_section(q['sh_info']);name=s.name.replace('.text.','')
   if name not in code_map:continue
   base=code_map[name]
   for v in q.iter_relocations():
    sym=e.get_section(q['sh_link']).get_symbol(v['r_info_sym']);off=v['r_offset'];a=base+off
    if v['r_info_type']==10:
     i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert sym.name in code_map and i.mnemonic=='bl' and i.operands[0].imm==code_map[sym.name];evidence.append({'kind':'BL','address':hex(a),'symbol':sym.name,'target':hex(code_map[sym.name])})
    elif v['r_info_type']==2:
     key=sym.name if sym.name else e.get_section(sym['st_shndx']).name;assert key in data_map;assert s.data()[off:off+4]==bytes(4);value=int.from_bytes(b[a-0x3300:a-0x3300+4],'little');assert value==data_map[key]
     refs=[hex(i.address) for i in md.disasm(b[base-0x3300:base-0x3300+off],base) if i.mnemonic=='ldr' and len(i.operands)>1 and i.operands[1].type==3 and i.operands[1].mem.base==11 and ((i.address+4)&~3)+i.operands[1].mem.disp==a]
     assert refs,(key,hex(a));evidence.append({'kind':'literal','address':hex(a),'source_symbol_or_section':key,'value':hex(value),'PC_loads':refs})
    else:raise AssertionError(v['r_info_type'])
 shutil.copyfile(O/(label+'.ld'),out/'link.ld');objects=['/input/public.o']
 if label=='flash':shutil.copyfile(R/'g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o',out/'assembly.o');objects.append('/out/assembly.o')
 if label=='ilo':
  for n in ['uidiv.o','zero.o']:shutil.copyfile(R/'g2/analysis/touch-libgcc14-division-2026-10-09/outputs'/n,out/n);objects.append('/out/'+n)
 argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld',*objects,'-o','/out/linked.elf'];p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
 with (out/'linked.elf').open('rb') as f:
  e=ELFFile(f)
  for name,a,n,dependency in sections:
   data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'dependency':dependency,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
 runs.append({'group':label,'argv':argv,'diagnostics':p.stderr,'original_relocation_evidence':evidence,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'link_script_sha256':sha(O/(label+'.ld')),'linked_elf_sha256':sha(out/'linked.elf')});(O/'linked-results.json').write_text(json.dumps({'runs':runs,'new_selected_candidates':8,'new_selected_candidate_bytes':1004,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'Static source comparators; memcpy remains stock-call-bound external, libgcc is binary-provider comparator, source-complete firmware/composition/physical state not established.'},indent=2)+'\n');print(label,[(x['section'],x['exact']) for x in rows],flush=True)
