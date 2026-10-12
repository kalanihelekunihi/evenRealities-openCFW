#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32cffc(uintptr_t,uintptr_t);
static uintptr_t allocated;static unsigned sends,timings;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==8);return allocated;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==123&&p==0x820000);sends++;return 9;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t n,uint32_t u){assert(n==800&&u==291);timings++;return 0x234;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805c70=0x810000-912;*(uint32_t*)0x805cac=0x830000;*(uint8_t*)0x805b18=123;*(uint32_t*)0x805a94=0xffffffff;*(uint32_t*)0x805a98=0xffffffff;*(uint32_t*)0x80281c=0x6a8;*(uint32_t*)0x802820=0x1bef;*(uint8_t*)0x810006=4;*(uint8_t*)0x810302=1;*(uint8_t*)0x810301=0;*(uint16_t*)0x810214=291;for(unsigned n=0;n<256;n++)for(unsigned fail=0;fail<2;fail++)for(unsigned enable=0;enable<2;enable++){allocated=fail?0:0x820000;*(uint8_t*)0x830044=n;*(uint8_t*)0x805a85=enable?128:0;unsigned oldsend=sends,oldtime=timings;assert(opencfw_em9305_mode_callback_32cffc(0x810000,0)==(enable?0x234:800));assert(sends==oldsend+!fail&&timings==oldtime+enable);assert(*(uint8_t*)0x810216==1&&*(uint32_t*)0x810218==(0x6a8&0xf787cf2f)&&*(uint32_t*)0x81021c==0x1bef);assert(*(uint8_t*)0x810050==1&&*(uint8_t*)0x810051==1);if(!fail){unsigned selected=(uint8_t)(n+105)>=110?n:150;assert(*(uint16_t*)0x820000==1&&*(uint16_t*)0x820002==0x6c01&&*(uint8_t*)0x820004==1&&*(uint8_t*)0x820005==selected&&*(uint8_t*)0x820006==selected);}}puts("PASS1024 callback event/timing paths; host XBFU model");}
