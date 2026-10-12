#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
extern uint32_t opencfw_em9305_init_lower_307ec8(uint32_t);
void opencfw_em9305_init_callback_30e840(void){}
void opencfw_em9305_init_callback_32b61c(void){}
void opencfw_em9305_init_callback_32beb0(void){}
void opencfw_em9305_init_callback_32bfc4(void){}
void opencfw_em9305_init_callback_31ae84(void){}
void opencfw_em9305_init_callback_304430(void){}
void opencfw_em9305_init_callback_3044e8(void){}
void opencfw_em9305_init_callback_3043ac(void){}
void opencfw_em9305_init_callback_304468(void){}
void opencfw_em9305_init_callback_3183ec(void){}
void opencfw_em9305_init_callback_31836c(void){}
void opencfw_em9305_init_callback_3245ec(void){}
void opencfw_em9305_init_callback_32468c(void){}
void opencfw_em9305_init_callback_324698(void){}
void opencfw_em9305_init_callback_31810c(void){}
void opencfw_em9305_init_callback_31807c(void){}
void opencfw_em9305_init_callback_318168(void){}
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
int main(void){assert(mmap((void *)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);for(unsigned version=0;version<256;version++){memset((void *)0x800000,0xa5,0x10000);W(0x805cac)=0x809000;B(0x809004)=version;uint32_t old=0x87654321;W(0x805b34)=old;uint32_t got=opencfw_em9305_init_lower_307ec8(0xdeadbeef);assert(got==(version>=13?(old|2048):version));assert(W(0x805b34)==(version>=13?(old|2048):old));
assert(W(0x805cdc)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_30e840);
assert(W(0x805cc4)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32b61c);
assert(W(0x805cc8)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32beb0);
assert(W(0x805ccc)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32bfc4);
assert(W(0x805c74)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31ae84);
assert(W(0x805c20)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_304430);
assert(W(0x805c28)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3044e8);
assert(W(0x805c1c)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3043ac);
assert(W(0x805c24)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_304468);
assert(W(0x805c60)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3183ec);
assert(W(0x805c5c)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31836c);
assert(W(0x805c9c)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3245ec);
assert(W(0x805ca0)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32468c);
assert(W(0x805ca4)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_324698);
assert(W(0x805248)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31810c);
assert(W(0x80299c)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31807c);
assert(W(0x8028ac)==(version>=13?(uint32_t)(uintptr_t)opencfw_em9305_init_callback_318168:0xa5a5a5a5u));}puts("PASS 256 final initializer versions and identities");}
