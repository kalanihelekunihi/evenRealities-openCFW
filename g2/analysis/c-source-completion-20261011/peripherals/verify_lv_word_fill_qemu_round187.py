from pathlib import Path
import tempfile,subprocess,json,hashlib,sys
BASE=Path(__file__).parent;ROOT=BASE.parents[2];D=BASE/'root-lv-word-fill-round187';SRC=D/'candidate.c';STOCK=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
assert hashlib.sha256(STOCK.read_bytes()[32:]).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 if '--selected' in sys.argv:
  selected=(ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d555c..4d558e;');fixture=t/'selected-fill.c';fixture.write_text('#include <stdint.h>\n'+selected[a:]);SRC=fixture
 (t/'start.S').write_text('.syntax unified\n.thumb\n.text\n.global reset_entry\n.thumb_func\nreset_entry: ldr sp,=0x02000000\nbl main\nb .\n')
 (t/'oracle.S').write_text('.section .stock,"ax"\n.incbin "'+str(STOCK)+'",32\n')
 (t/'module.ld').write_text('ENTRY(reset_entry)\nSECTIONS{.text 0x100000 : {*(.text*) *(.rodata*)}.stock 0x438000 : {KEEP(*(.stock))}.data 0x01000000 : {*(.data*)}.bss : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}')
 (t/'harness.c').write_text('#include <stdint.h>\nextern void *audio_uart_lv_word_fill_4d555c(void*,uint32_t,uint32_t);\nextern void audio_uart_lv_memzero_48949c(void*,uint32_t);\nstatic void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("svc 0xab":"+r"(r0):"r"(r1):"memory");}\nstatic void print(const char*s){host(4,(uintptr_t)s);}\nstatic uint8_t a[512] __attribute__((aligned(16))),b[512] __attribute__((aligned(16)));\nint main(void){unsigned failures=0,count=0;const uint32_t patterns[]={0,1,255,0x12345678,0x80000000,0xffffffff};\nfor(unsigned zero=0;zero<2;zero++)for(unsigned n=0;n<=128;n++)for(unsigned j=0;j<6;j++){\nfor(unsigned k=0;k<512;k++)a[k]=b[k]=165;\nuintptr_t nr=0,cr=0;\nif(zero){((void(*)(void*,uint32_t))(uintptr_t)0x48949d)(a,n);audio_uart_lv_memzero_48949c(b,n);}\nelse{nr=(uintptr_t)((void*(*)(void*,uint32_t,uint32_t))(uintptr_t)0x4d555d)(a,n,patterns[j])-(uintptr_t)a;cr=(uintptr_t)audio_uart_lv_word_fill_4d555c(b,n,patterns[j])-(uintptr_t)b;}\nif(nr!=cr)failures++;\nfor(unsigned k=0;k<512;k++)if(a[k]!=b[k]){failures++;break;}count++;\n}\nprint(failures?"FAIL_WORD_FILL\\n":"PASS_WORD_FILL_1548\\n");unsigned quit[2]={0x20026,failures};host(0x20,(uintptr_t)quit);for(;;){} }\n')
 flags=['--target=arm-none-eabi','-mcpu=cortex-a9','-mthumb','-mfpu=none','-mfloat-abi=soft','-fno-vectorize','-fno-slp-vectorize','-O2','-ffreestanding','-fno-builtin'];objects=[]
 for source in [t/'start.S',t/'oracle.S',t/'harness.c',SRC]:
  obj=t/(source.name+'.o');subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True);objects.append(str(obj))
 elf=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),*objects,'-o',str(elf)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','versatilepb','-cpu','cortex-a9','-m','64M','-audio','none','-nographic','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf)],capture_output=True,text=True,timeout=30)
 output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);
 assert result.returncode==0 and 'PASS_WORD_FILL_1548' in output
 receipt={'status':'PASS_INDEPENDENT_QEMU_WORD_FILL_ZERO','cases':1548,'selected':'--selected' in sys.argv,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Optimized O2 Cortex-A9 Thumb independent execution, aligned lengths0..128/six patterns/full512bytes and fill advanced pointer compared; zero void return ignored.','Bus/store trace and unaligned fault behavior unproved; physical G2 M55/cache/fullimage behavior unqualified. Native bytes used only in temporary authenticated test oracle.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
