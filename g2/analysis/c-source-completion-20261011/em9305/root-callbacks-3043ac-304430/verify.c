#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <sys/mman.h>
#include <string.h>
uint32_t opencfw_em9305_init_callback_3043ac(uint32_t,uintptr_t,uint32_t);
uint32_t opencfw_em9305_init_callback_304430(uint32_t,uintptr_t,uint32_t);
static uintptr_t ctx=0x810000u;static unsigned cancels,binds,requests,fills,records,cbs;
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t x){(void)x;++cancels;return 999;}
uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t p){assert(p==0x8015ccu);++binds;return 888;}
uint32_t opencfw_em9305_radio_request_30faec(uintptr_t p,uint32_t mode){assert(mode==257&&p==0x12345678u);++requests;return 777;}
void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){assert(v==0&&n==20);++fills;return memset(p,0,n);}
uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t p){for(unsigned i=0;i<20;i++)assert(((uint8_t*)p)[i]==0);++records;return 666;}
static uint32_t cb(uint32_t owner,uint32_t index,uintptr_t identity){assert(owner==42&&index==2&&identity==(uintptr_t)cb);++cbs;*(uint8_t*)(ctx+225)=3;return 555;}
static void setup(void){memset((void*)ctx,0,512);cancels=binds=requests=fills=records=cbs=0;*(uint8_t*)(ctx+228)=5;*(uint8_t*)(ctx+226)=4;for(unsigned i=0;i<4;i++)*(uint32_t*)(ctx+208+4*i)=0x12345678;*(uint32_t*)(ctx+248)=10;*(uint32_t*)(ctx+256)=3;*(uint32_t*)(ctx+236)=100;*(uint32_t*)(ctx+244)=200;}
int main(void){assert(mmap((void*)0x801000u,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x801000u);assert(mmap((void*)ctx,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)ctx);
setup();assert(opencfw_em9305_init_callback_3043ac(42,ctx,123)==123);assert(cancels==1&&binds==1&&requests==1);assert(*(uint8_t*)0x8015c4u==1);assert(*(uint32_t*)0x8015d8u==6&&*(uint32_t*)0x8015d4u==307);
setup();*(uint8_t*)(ctx+224)=4;assert(opencfw_em9305_init_callback_3043ac(42,ctx,123)==1);assert(*(uint8_t*)(ctx+224)==5&&fills==1&&records==1&&binds==0);
setup();*(uint8_t*)(ctx+225)=4;assert(opencfw_em9305_init_callback_3043ac(42,ctx,123)==1);assert(fills==1&&records==1);
setup();*(uint32_t*)(ctx+208)=0;assert(opencfw_em9305_init_callback_3043ac(42,ctx,123)==1);assert(fills==1&&records==1);
setup();*(uint8_t*)(ctx+225)=2;*(uint32_t*)(ctx+164)=(uint32_t)(uintptr_t)cb;assert(opencfw_em9305_init_callback_304430(42,ctx,123)==123);assert(cbs==1&&cancels==2&&*(uint8_t*)(ctx+225)==0&&requests==1);
setup();assert(opencfw_em9305_init_callback_304430(42,ctx,123)==123);assert(cbs==0&&cancels==2&&*(uint8_t*)(ctx+225)==1&&requests==1);
return 0;}
