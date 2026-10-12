from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native completion332cd0'):s.index('/* Native continuation332d2c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t p=0x8058dc;unsigned n=0;uint32_t values[]={0,1,0x7fffffff,0x80000000,0xffffffff};uint16_t counts[]={0,1,65534,65535};
for(unsigned event=0;event<6;event++)for(unsigned st=0;st<4;st++)for(unsigned limit=0;limit<5;limit++)for(unsigned ci=0;ci<4;ci++)for(unsigned li=0;li<5;li++)for(unsigned di=0;di<5;di++){uint32_t low=values[li],delta=values[di],high=values[(li+di)%5];*(uint8_t *)p=st;*(uint16_t *)(p+2)=limit;*(uint16_t *)(p+6)=counts[ci];*(uint16_t *)(p+8)=7;*(uint16_t *)(p+10)=9;*(uint16_t *)(p+20)=65535;*(uint32_t *)(p+12)=low;*(uint32_t *)(p+16)=high;uint64_t expected=((uint64_t)high<<32)|low;if(event==0)expected+=(uint64_t)(int64_t)(int32_t)delta;unsigned a=event==0?(uint16_t)(counts[ci]+1):counts[ci],b=event==4?8:7,c=event!=0&&event!=4?10:9;unsigned result=limit&&a+b+c>=limit?0:st==2;assert(opencfw_em9305_command_callback_332cd0(0,event,delta)==result);assert(*(uint16_t *)(p+6)==a&&*(uint16_t *)(p+8)==b&&*(uint16_t *)(p+10)==c&&*(uint16_t *)(p+20)==(event==0?0:65535));assert(*(uint32_t *)(p+12)==(uint32_t)expected&&*(uint32_t *)(p+16)==(uint32_t)(expected>>32));n++;}
printf("PASS %u\n",n);}
''';p=Path(__file__).with_name('command-completion-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/c && /tmp/c'],text=True);print(a.strip());p.with_name('command-completion-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual callback C, all event classes, counter wrap and signed64 carry/borrow, count-limit state returns. No hardware/interrupt runtime proof.'},indent=2)+'\n')
