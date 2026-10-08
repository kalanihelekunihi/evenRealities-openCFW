/* Locked42e8d0/42ea32 reconstruction. INFO dispatch source is reused;
 * resident ROM/peripheral behavior is external, never replaced as firmware. */
#include "adc_context.h"
#include "../application_storage/device_mode_wait.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
#define POOL 0x20026df0u
#define CACHE 0x200267f8u
#define TRIMS 0x20026fc0u
#define PAIR 0x20026fe0u
__attribute__((section(".bss.boot_adc_context_pool"),used))
volatile opencfw_boot_adc_context opencfw_boot_adc_context_pool;
NI uint32_t opencfw_bl_adc_context_initialize(uint32_t module,uint32_t *context_out) {
    if(module!=0)return 5;
    if(!context_out)return 6;
    if(R(POOL)&0x01000000u)return 7;
    R(POOL)|=0x01000000u;
    R(POOL)=(R(POOL)&0xff000000u)|0x00afafafu;
    R(POOL+4)=module;
    R(0x2002702cu)=0;
    *(volatile uint32_t *)context_out=POOL;
    uint32_t status;
    if(R(CACHE)==0x1f01600du) {
        R(TRIMS)=R(CACHE+0x38);R(TRIMS+4)=R(CACHE+0x3c);R(TRIMS+8)=R(CACHE+0x40);status=0;
    } else {
        status=opencfw_boot_device_mode_wait(1,0x240,1,(volatile uint32_t *)(uintptr_t)TRIMS);
        status|=opencfw_boot_device_mode_wait(1,0x241,1,(volatile uint32_t *)(uintptr_t)(TRIMS+4));
        status|=opencfw_boot_device_mode_wait(1,0x242,1,(volatile uint32_t *)(uintptr_t)(TRIMS+8));
    }
    if(!R(TRIMS)||!R(TRIMS+4)||!R(TRIMS+8)||status) {
        R(TRIMS)=0x4395c000u;R(TRIMS+4)=0x3f839874u;R(TRIMS+8)=0xbb8c47a1u;B(TRIMS+12)=0;
    } else B(TRIMS+12)=1;
    if(R(CACHE)==0x1f01600du) {
        R(PAIR+4)=R(CACHE+0x48);R(PAIR)=R(CACHE+0x4c);status=0;
    } else {
        status=opencfw_boot_device_mode_wait(1,0x24a,1,(volatile uint32_t *)(uintptr_t)(PAIR+4));
        status|=opencfw_boot_device_mode_wait(1,0x24b,1,(volatile uint32_t *)(uintptr_t)PAIR);
    }
    R(0x4002010cu)&=~1u;
    B(0x20027199u)=R(PAIR+4)&&R(PAIR)&&status==0 ? 1u:0u;
    return 0;
}
NI uint32_t opencfw_bl_adc_reset(uint32_t context) {
    if(!context || (R(context)&0x01ffffffu)!=0x01afafafu)return 2;
    R(context)&=~0x01000000u;
    R(context)&=0xff000000u;
    R(context+4)=0;
    return 0;
}
