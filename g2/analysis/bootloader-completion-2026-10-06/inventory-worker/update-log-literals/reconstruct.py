from pathlib import Path
import re,json,hashlib
C=Path('g2/components/bootloader/update_core/log_literals');N=Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/update-log-literals');text=Path('g2/components/bootloader/update_core/update_core.c').read_text();addresses={0x433fe0,0x4310c4}
for m in re.finditer(r'(?:LOG|ERROR)\((0x[0-9a-f]+)u,0x[0-9a-f]+u,(0x[0-9a-f]+)u',text):addresses.update(int(x,16) for x in m.groups())
b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();rows=[];s='/* Reconstructed readonly diagnostics used by update_core.c.\n * Fixed source pointer ABI; no original executable bytes. */\n'
for a in sorted(addresses):
 o=a-0x410000;v=b[o:b.index(b'\0',o)];name=f'opencfw_update_log_literal_{a:x}';section=f'.boot_update_log_{a:x}';s+=f'__attribute__((section("{section}"),used)) const char {name}[]={json.dumps(v.decode())};\n';rows.append(dict(address=a,bytes=len(v)+1,text=v.decode(),symbol=name,section=section,sha256=hashlib.sha256(v+b'\0').hexdigest()))
(C/'log_literals.c').write_text(s);(N/'literal-manifest.json').write_text(json.dumps(dict(original_sha256=hashlib.sha256(b).hexdigest(),source_sha256=hashlib.sha256(s.encode()).hexdigest(),literals=rows,total_literal_bytes=sum(r['bytes'] for r in rows),limits='15 exact NUL-terminated strings; alignment gaps and neighboring assets not included or claimed.'),indent=2)+'\n');(N/'reconstruct.py').write_bytes(Path('/tmp/opencfw-update-log-literals.py').read_bytes());print('literal bytes',sum(r['bytes'] for r in rows))
