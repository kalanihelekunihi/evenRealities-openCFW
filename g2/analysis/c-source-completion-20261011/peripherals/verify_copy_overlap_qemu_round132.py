"""Independent QEMU Thumb oracle, executable stock confined to temporary test ELF."""
from pathlib import Path
import tempfile,subprocess,json,hashlib,sys
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-copy-overlap-round132/copy_candidate.c';FORWARD=ROOT/'components/audio/queue_cmsis_offline/cmsis.c';STOCK=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
baseline='--baseline' in sys.argv
if baseline or '--selected' in sys.argv:SRC=ROOT/'components/audio/uart_thread_source_candidate/byte_copy.c'
assert hashlib.sha256(STOCK.read_bytes()[32:]).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);(t/'start.S').write_text('.syntax unified\n.thumb\n.text\n.global reset_entry\n.thumb_func\nreset_entry: ldr sp,=0x02000000\nbl main\nb .\n')
 (t/'oracle.S').write_text('.section .stock,"ax"\n.incbin "'+str(STOCK)+'",32\n')
 (t/'module.ld').write_text('ENTRY(reset_entry)\nSECTIONS{.text 0x100000 : {*(.text*) *(.rodata*)}.stock 0x438000 : {KEEP(*(.stock))}.data 0x01000000 : {*(.data*)}.bss : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}')
 (t/'forward.c').write_text('#include <stdint.h>\nvoid *audio_queue_copy_bytes('+FORWARD.read_text().split('void *audio_queue_copy_bytes(',1)[1])
 (t/'harness.c').write_text(r'''#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("svc 0xab":"+r"(r0):"r"(r1):"memory");}
static void print(const char*s){host(4,(uintptr_t)s);}
static void hex(unsigned x){char b[9];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(x>>(28-4*i))&15];b[8]=0;print(b);}
static uint8_t buf[1024],saved[1024];
static void fill(void){for(unsigned i=0;i<1024;i++)buf[i]=(uint8_t)i;}
int main(void){unsigned count=0,failures=0;const int delta[]={-96,-17,-8,-4,-3,-2,-1,0,1,2,3,4,8,17,96};
for(unsigned sa=0;sa<4;sa++)for(unsigned j=0;j<15;j++)for(unsigned n=0;n<=96;n++){
unsigned source=256+sa,destination=source+delta[j];
fill();((void (*)(void*,const void*,uint32_t))(uintptr_t)0x439be5)(buf+destination,buf+source,n);
for(unsigned k=0;k<1024;k++)saved[k]=buf[k];fill();audio_uart_checksum_copy(buf+destination,buf+source,n);
for(unsigned k=0;k<1024;k++)if(saved[k]!=buf[k]){if(!failures){print("FIRST_MISMATCH ");hex(sa);print(" ");hex((unsigned)delta[j]);print(" ");hex(n);print("\n");}failures++;break;}count++;
}
print(failures?"FAILED_COPY\n":"PASS_COPY_5820\n");print("MISMATCHES ");hex(failures);print("\n");unsigned quit[2]={0x20026,failures};host(0x20,(uintptr_t)quit);for(;;){} }
''')
 flags=['--target=arm-none-eabi','-mcpu=cortex-a9','-mthumb','-mfpu=none','-mfloat-abi=soft','-fno-vectorize','-fno-slp-vectorize','-O2','-ffreestanding','-fno-builtin'];objects=[]
 for source in [t/'start.S',t/'oracle.S',t/'harness.c',SRC]:
  obj=t/(source.name+'.o');subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True);objects.append(str(obj))
 elf=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),*objects,'-o',str(elf)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','versatilepb','-cpu','cortex-a9','-m','64M','-audio','none','-nographic','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf)],capture_output=True,text=True,timeout=30)
 output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);
 if baseline:
  assert result.returncode!=0 and 'FIRST_MISMATCH' in output
  d=BASE/'root-copy-overlap-round132';(d/'baseline-mismatch.json').write_text(json.dumps({'status':'EXISTING_BYTE_LOOP_NATIVE_OVERLAP_MISMATCH','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'output':output},indent=2)+'\n');raise SystemExit(0)
 assert result.returncode==0 and 'PASS_COPY_5820' in output
 receipt={'status':'PASS_INDEPENDENT_QEMU_COPY_OVERLAP','cases':5820,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(STOCK.read_bytes()[32:]).hexdigest(),'limits':['Full1024byte buffer compared across source alignments0..3,lengths0..96 and fifteen deltas including forward/backward overlap; native return and bus timing not compared.','Independent Cortex-A9 Thumb execution; physical G2 startup and connected Unicorn mismatch remain unqualified. Native executable bytes temporary test oracle only.']};d=BASE/'root-copy-overlap-round132';d.mkdir(exist_ok=True);(d/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
