#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
command_script=ROOT/'g2/components/case/source_candidate_20261010/build.py';report=HERE/'command-evidence';report.mkdir(exist_ok=True)
s=command_script.read_text().replace("REPORT=ROOT/'g2/analysis/case-source-candidate-round2-20261010'","REPORT=OUTPUT/'command-evidence'").replace("OUT=HERE/'build'","OUT=OUTPUT/'command-build'")
exec(compile(s,str(command_script),'exec'),{'__file__':str(command_script),'OUTPUT':HERE})
startup=HERE/'startup.o';subprocess.run([sys.executable,str(ROOT/'g2/analysis/c-source-completion-20261011/m0/build_startup_candidate.py'),'--output',str(startup)],check=True)
command=HERE/'command-build/libcase_source_candidate.a';reloc=HERE/'case.o';subprocess.run(['arm-none-eabi-ld','-r','--whole-archive',str(command),'--no-whole-archive',str(startup),'-o',str(reloc)],check=True)
undefined=subprocess.check_output(['arm-none-eabi-nm','-u',str(reloc)],text=True);assert not undefined.strip(),undefined
layout=ROOT/'g2/analysis/c-source-completion-20261011/m0/case_clean_experimental_layout.ld';elf=HERE/'case.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(reloc),'-o',str(elf)],check=True)
r={'status':'PASS_CURRENT_CASE_ABI_GRAPH_LINK','command_receipt':str((report/'receipt.json').relative_to(ROOT)),'command_receipt_sha256':sha(report/'receipt.json'),'startup_receipt':str(Path(str(startup)+'.receipt.json').relative_to(ROOT)),'startup_receipt_sha256':sha(Path(str(startup)+'.receipt.json')),'relocatable_sha256':sha(reloc),'elf_sha256':sha(elf),'undefined_symbols':[],'layout_sha256':sha(layout),'limits':['Current source graph/ABI binding only; diagnostic absolute ELF remains different from locked image and not hardware-ready.','Historical selected manifest and archive remain unchanged; this producer has its own current source receipt.']}
(HERE/'build-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
