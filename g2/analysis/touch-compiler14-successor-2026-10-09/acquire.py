from pathlib import Path
import json,hashlib,urllib.request,tarfile
O=Path(__file__).resolve().parent;R=O.parents[2]
url='https://gitlab.arm.com/api/v4/projects/tooling%2Fgnu-toolchains-for-arm/packages/generic/gnu-toolchain/14.2.rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi.tar.xz'
expected='62a63b981fe391a9cbad7ef51b17e49aeaa3e7b0d029b36ca1e9c3b2a9b78823'
receipt=R/'g2/analysis/source-discovery-parallel-2026-10-09/arm-14.2.rel1-x86_64-arm-none-eabi.sha256asc'
assert hashlib.sha256(receipt.read_bytes()).hexdigest()=='0058e16f204afcb764a38af718b835e1b3f86e52aef1d0518c8f4397df69b2a7'
assert expected in receipt.read_text()
out=O/'tools/14.2.Rel1';out.mkdir(parents=True,exist_ok=True);archive=out/'arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi.tar.xz'
if not archive.exists():
 with urllib.request.urlopen(url) as src,archive.open('wb') as dst:
  while chunk:=src.read(1024*1024):dst.write(chunk)
actual=hashlib.sha256(archive.read_bytes()).hexdigest();assert actual==expected
with tarfile.open(archive) as tar:tar.extractall(out,filter='data')
gcc=next(out.glob('*/bin/arm-none-eabi-gcc'))
(O/'acquisition.json').write_text(json.dumps([{'version':'14.2.Rel1','url':url,'archive_sha256':actual,'gcc':str(gcc.relative_to(O)),'gcc_sha256':hashlib.sha256(gcc.read_bytes()).hexdigest(),'checksum_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'signature_verification':False}],indent=2)+'\n')
print('14.2 archive authenticated and extracted')
