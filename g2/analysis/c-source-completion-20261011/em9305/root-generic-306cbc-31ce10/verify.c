#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_callback_306cbc(uint32_t,uint32_t);
uint32_t opencfw_em9305_callback_31ce10(void);
static uintptr_t found;static uint32_t expected_id;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==expected_id);return found;}
int main(void){assert(mmap((void*)0x805000u,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x805000u);assert(mmap((void*)0x810000u,0x21000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x810000u);
 expected_id=0xffffffffu;found=0;assert(opencfw_em9305_callback_306cbc(expected_id,77)==66);
 found=0x810000u;for(unsigned flags=0;flags<256;flags++){*(uint8_t*)(found+32)=flags;*(uint8_t*)0x805400u=88;assert(opencfw_em9305_callback_306cbc(expected_id,0x12345678)==0);assert(*(uint8_t*)(found+2808)==0x78);assert(*(uint8_t*)0x805400u==((flags&16)?0x78:88));}
 *(uint32_t*)0x805cacu=0x810000u;*(uint32_t*)0x805c3cu=0;
 *(uint8_t*)0x810039u=0;assert(opencfw_em9305_callback_31ce10()==0);
 *(uint32_t*)0x805c3cu=0x811000u;
 for(unsigned count=1;count<256;count++){*(uint8_t*)0x810039u=count;for(unsigned i=0;i<256;i++){uintptr_t r=0x811000u+i*512u;*(uint8_t*)r=(i%3)!=0;*(uint8_t*)(r+3)=i%4;*(uint8_t*)(r+273)=0xaau;*(uint8_t*)(r+272)=77;*(uint8_t*)(r+274)=99;}assert(opencfw_em9305_callback_31ce10()==0);for(unsigned i=0;i<256;i++){uintptr_t r=0x811000u+i*512u;assert(*(uint8_t*)(r+273)==((i<count&&i%3!=0&&i%4==1)?0xab:0xaa));assert(*(uint8_t*)(r+272)==77&&*(uint8_t*)(r+274)==99);}}
 return 0;}
