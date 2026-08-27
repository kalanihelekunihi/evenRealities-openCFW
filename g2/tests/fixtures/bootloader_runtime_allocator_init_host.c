#include <stdint.h>
#include <string.h>
#define OPEN_CFW_ALLOCATOR_INIT_HOST 1
static uint8_t pool[32]; static void *stored; static uint32_t seq[3], n;
static uint32_t memset_size, memset_value, create_size; static uintptr_t args[6];
void *open_cfw_allocator_init_host_pool(void){return pool;}
void **open_cfw_allocator_init_host_handle(void){return &stored;}
void open_cfw_allocator_init_host_memset(void *p,uint32_t size,uint32_t value){seq[n++]=1;memset_size=size;memset_value=value;memset(p,0,sizeof(pool));}
void *open_cfw_allocator_init_host_create(void *p,uint32_t size){seq[n++]=2;create_size=size;return (uint8_t*)p+8;}
void open_cfw_allocator_init_host_log(uint32_t a,uintptr_t b,uintptr_t c,uintptr_t d,uint32_t e,uintptr_t f){seq[n++]=3;args[0]=a;args[1]=b;args[2]=c;args[3]=d;args[4]=e;args[5]=f;}
#include "../../components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"
uint32_t open_cfw_test_allocator_init(void){memset(pool,0xa5,sizeof(pool));stored=0;n=0;if(open_cfw_bootloader_allocator_init_41fd70()!=0)return 0;return n==3&&seq[0]==1&&seq[1]==2&&seq[2]==3&&memset_size==0x70800&&memset_value==0&&create_size==0x70800&&stored==pool+8&&args[0]==4&&args[1]==0x434144&&args[2]==0x4315c8&&args[3]==0x433ca4&&args[4]==0x13&&args[5]==0x434010;}
