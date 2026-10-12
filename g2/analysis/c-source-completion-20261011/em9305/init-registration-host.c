#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
void opencfw_em9305_init_registered_31e8fc(void){}
void opencfw_em9305_init_registered_321608(void){}
void opencfw_em9305_init_registered_32182c(void){}
void opencfw_em9305_init_registered_322d68(void){}
void opencfw_em9305_init_registered_32613c(void){}
void opencfw_em9305_init_registered_3263ec(void){}
void opencfw_em9305_init_registered_32ce04(void){}
void opencfw_em9305_init_registered_3266f8(void){}
void opencfw_em9305_init_registered_324fb4(void){}
#include "init-registration-prepared.c"
#define W(a) (*(uint32_t*)(uintptr_t)(a))
#define PTR(f) ((uint32_t)(uintptr_t)(f))
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(unsigned version=0;version<256;version++){
memset((void*)0x800000,0xa5,0x10000);W(0x805cac)=0x804000;*(uint8_t*)0x804004=version;W(0x805b30)=0x80000001;
if(opencfw_em9305_init_lower_307c18(7)!=(version<9?version:0x805b30)||W(0x805b30)!=(0x80000001u|(version>=9?1u<<13:0))||W(0x805228)||W(0x80297c)!=PTR(opencfw_em9305_init_registered_31e8fc)||W(0x80130c)!=PTR(opencfw_em9305_init_state_one_307cb8))abort();
cases++;
W(0x805b30)=0x80000001;if(opencfw_em9305_init_lower_307cc8(9)!=0x805b0c||W(0x805b30)!=(0x80000001u|(version>=9?1u<<13:0))||*(uint16_t*)0x805b22!=784||W(0x802984)!=PTR(opencfw_em9305_init_registered_321608)||W(0x805230)!=PTR(opencfw_em9305_init_registered_32182c))abort();
cases++;
W(0x805b30)=0x80000001;if(opencfw_em9305_init_lower_307d2c(8)!=(version<10?version:0x805b30)||W(0x805b30)!=(0x80000001u|(version>=10?1u<<25:0))||W(0x80522c)||W(0x802980)!=PTR(opencfw_em9305_init_registered_322d68))abort();
cases++;
*(uint8_t*)0x8051a4=version;if(opencfw_em9305_init_state_one_307cb8()!=(version==1))abort();
cases++;
}
if(opencfw_em9305_init_lower_307de8(7)!=0x8051f4||W(0x8052bc)!=PTR(opencfw_em9305_init_registered_32613c)||W(0x8052c0)!=PTR(opencfw_em9305_init_registered_3263ec)||W(0x8056d8)!=PTR(opencfw_em9305_init_registered_32ce04)||W(0x8052c4)!=PTR(opencfw_em9305_init_registered_3266f8)||W(0x8051f4)!=PTR(opencfw_em9305_init_registered_324fb4))abort();
cases++;
printf("PASS %u isolated registration/getter cases\n",cases);return 0;}
