#!/usr/bin/env python3
"""Link current source-built objects under explicit custom memory bounds."""
from pathlib import Path
import argparse,json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;A=argparse.ArgumentParser();A.add_argument('--output',type=Path,default=H/'build');args=A.parse_args();O=args.output.resolve();O.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=H.parent/'case-wave033-native-timer-message-width';receipt=P/'final/receipt.json';r=json.loads(receipt.read_text())
for row in r['sources']:
 assert sha(R/row['source'])==row['source_sha256'];assert sha(R/row['object'])==row['object_sha256']
merged=P/'final/merged-lto.o';assert sha(merged)==r['merged_object_sha256'];cmd=r['link_command'].copy();i=cmd.index('-T');cmd[i+1]=str(H/'layout.ld');cmd[-1]=str(O/'case.elf');p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(O/'case.elf'),str(O/'case-custom.bin')],check=True)
rr={'status':'LINKED_SOURCE_CUSTOM_MEMORY_CONTRACT','source_build_receipt':str(receipt.relative_to(R)),'source_build_receipt_sha256':sha(receipt),'merged_source_object_sha256':sha(merged),'layout_sha256':sha(H/'layout.ld'),'link_command':cmd,'ELF_sha256':sha(O/'case.elf'),'raw_binary_sha256':sha(O/'case-custom.bin'),'raw_binary_bytes':(O/'case-custom.bin').stat().st_size,'undefined_symbols':subprocess.check_output(['arm-none-eabi-nm','-u',str(O/'case.elf')],text=True),'limits':['Raw source-derived diagnostic binary only, no stock package envelope or flashing operation.','Link bounds and RAM initialization contract do not prove wholebody/computedroot/ambientstack/peripheral readiness.','No prebuilt firmware/runtime inputs; allobjects hashmatch current401unit source compilation.']};(O/'receipt.json').write_text(json.dumps(rr,indent=2)+'\n');print(rr['status'],rr['raw_binary_bytes'])
