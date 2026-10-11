/* SPDX-License-Identifier: MIT
 * Experimental whole-control reduction of stock application entry 0x0800a598.
 * The boot subsystem, option-byte programmer, services and product messages
 * remain typed calls. The final native loop is intentionally nonreturning.
 */
#include <stdint.h>
extern void case_boot_clock_restore(void);      /* 0x08004eec */
extern void case_boot_input_initialize(void);    /* 0x08008438 */
extern void case_boot_pin_initialize(void);      /* 0x08006a40 */
extern void case_boot_power_initialize(void);    /* 0x08002888 */
extern void case_boot_bus_initialize(void);      /* 0x08006bb0 */
extern void case_boot_sensor_initialize(void);   /* 0x08006c00 */
extern void case_boot_console_initialize(void);  /* 0x080068f0 */
extern void case_boot_read_option_words(uint32_t *words); /* 0x08004a00 */
extern void case_boot_log(uint32_t message,uint32_t a,uint32_t b); /* 0x08009170; product strings external */
extern void case_boot_option_prepare(void);      /* 0x08004bf4 */
extern void case_boot_option_unlock(void);       /* 0x08004b6c */
extern uint32_t case_boot_option_write(const uint32_t *words); /* 0x08004a6c */
extern void case_boot_option_commit_a(void);     /* 0x08004b3c */
extern void case_boot_option_commit_b(void);     /* 0x08004b50 */
extern void case_boot_option_commit_c(void);     /* 0x08004b20 */
extern void case_application_initialize_2fc8(void);
extern int32_t case_boot_service_start(void);    /* 0x0800a8d8 */
extern void case_boot_transport_start(void);     /* 0x08006968 */
extern void case_boot_scheduler_start(void);     /* 0x0800a900 */
static uint32_t silent(void){return *(volatile uint8_t *)(uintptr_t)0x200000bfu;}
static void logline(uint32_t id,uint32_t a,uint32_t b)
{if(silent()==0u){case_boot_log(id,a,b);case_boot_log(0x0800a70cu,0u,0u);}}
__attribute__((noreturn)) void case_application_entry_a598(void)
{
    case_boot_clock_restore();case_boot_input_initialize();case_boot_pin_initialize();
    case_boot_power_initialize();case_boot_bus_initialize();case_boot_sensor_initialize();
    case_boot_console_initialize();
    uint32_t option[7];
    /* At cold reset CRT zeroes 0x200001a4..0x20002c88. Native entry uses
     * SP=0x20002c88-32; words[1] is untouched RAM at 0x20002c70. */
    option[1]=0u;
    case_boot_read_option_words(option);
    if((option[6]&0x1000000u)!=0u || option[4]!=0xaau){
        logline(0x0800a6dcu,option[6],0u);
        option[0]=6u;option[6]=(option[6]&0xfeffff00u)|0xaau;option[4]=0xaau;
        case_boot_option_prepare();case_boot_option_unlock();(void)case_boot_option_write(option);
        case_boot_option_commit_a();case_boot_option_commit_b();case_boot_option_commit_c();
    }else logline(0x0800a710u,option[6],0xaau);
    volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0x40021000u;
    clock[15]|=0x40021000u<<16;
    volatile uint8_t *wake=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint32_t *power=(volatile uint32_t *)(uintptr_t)0x40007000u;
    wake[0]=0u;
    if(((~power[4])&(1u<<8))==0u){
        power[6]=0x10100u;
        if(((~power[4])&(1u<<3))==0u){power[6]=0x10008u;wake[0]=1u;logline(0x0800a74cu,0u,0u);}
        if(((~power[4])&(1u<<5))==0u){power[6]=0x10020u;wake[0]=2u;logline(0x0800a760u,0u,0u);}
        if(wake[0]==0u){wake[0]=3u;logline(0x0800a774u,0u,0u);}
    }else logline(0x0800a788u,0u,0u);
    case_application_initialize_2fc8();(void)case_boot_service_start();
    case_boot_transport_start();case_boot_scheduler_start();
    for(;;)__asm__ volatile("" ::: "memory");
}
