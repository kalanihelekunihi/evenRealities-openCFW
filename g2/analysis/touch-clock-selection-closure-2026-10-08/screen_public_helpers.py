"""Screen two verbatim public helper bodies in an explicit macro environment."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True);s=a.source.read_text();functions={}
for name in ['Cy_CapSense_GetPolySize','Cy_CapSense_GetLfsrDitherVal']:
 match=re.search(r'uint32_t\s+'+name+r'\s*\([^;{]*\)\s*\{',s);start=match.start();i=match.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 functions[name]=s[start:i]
c=a.output/'public_helpers.c';c.write_text('#include <stdint.h>\n#define CY_CAPSENSE_LFSR_BITS_RANGE_MASK (0x03u)\n'+'\n'.join(functions.values())+'\n');fw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:];rows=[]
for opt in ['Og','O1','O2','Os']:
 obj=a.output/(opt+'.o');subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-'+opt,'-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(c),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  e=ELFFile(f)
  for name,start,extent in [('Cy_CapSense_GetPolySize',0x6220,28),('Cy_CapSense_GetLfsrDitherVal',0x6262,14)]:
   sec=e.get_section_by_name('.text.'+name);data=sec.data();stock=fw[start-0x3300:start-0x3300+extent];rel=e.get_section_by_name('.rel.text.'+name);rows.append({'function':name,'optimization':opt,'stock_address':hex(start),'stock_extent':extent,'public_extent':len(data),'matching_offsets':[hex(0x3300+i) for i in range(len(fw)-len(data)+1) if fw[i:i+len(data)]==data],'exact':data==stock,'relocations':rel.num_relocations() if rel else 0,'public_sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
receipt={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'source_path':str(a.source),'pin':'247a9a0f79eb976f144f5fbeb29488c1c2606517','macro_environment':{'CY_CAPSENSE_LFSR_BITS_RANGE_MASK':'0x03u'},'extracted_file_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'comparisons':rows,'limits':['Verbatim selected public function bodies, synthesized minimal translation unit; not a complete SDK build.','No claim that compiler/release is uniquely identified.']};(D/'public-helper-screen.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(rows,indent=2))
