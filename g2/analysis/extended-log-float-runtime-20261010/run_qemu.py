"""Reproduce M55 FP64 capability and stock-address mapping check."""
import hashlib,json,subprocess,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
src=HERE/'fp64_probe.S';obj=HERE/'fp64_probe.o';elf=HERE/'fp64_probe.elf'
ota=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
raw=ota.read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-T',str(HERE/'link.ld'),str(obj),'-o',str(elf)],check=True)
version=subprocess.check_output(['qemu-system-arm','--version'],text=True).splitlines()[0]
run=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-nographic','-semihosting','-kernel',str(elf)],capture_output=True,text=True,timeout=5)
assert run.returncode==0 and 'M55 FP64 PASS' in run.stdout+run.stderr,(run.returncode,run.stdout,run.stderr)
with tempfile.TemporaryDirectory() as t:
    stripped=Path(t)/'main-stripped.bin';stripped.write_bytes(raw)
    monitor=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-S','-monitor','stdio','-device',f'loader,file={stripped},addr=0x438000','-kernel',str(elf)],input='xp /4wx 0x438000\nquit\n',capture_output=True,text=True,timeout=5)
    assert monitor.returncode==0 and '00438000: Cannot access memory' in monitor.stdout
receipt={'status':'PASS','qemu_version':version,'probe_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'image_sha256':hashlib.sha256(raw).hexdigest(),
         'fp64_probe_output':(run.stdout+run.stderr).strip(),
         'stock_base_monitor':'00438000: Cannot access memory',
         'limit':'QEMU MPS3 AN547 executes standalone M55 FP64 but cannot map stock main image at its fixed 0x438000 address via loader. No stock formatter execution.'}
(HERE/'qemu_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
