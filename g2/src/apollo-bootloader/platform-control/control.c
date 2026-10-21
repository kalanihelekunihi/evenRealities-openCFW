/* SPDX-License-Identifier: MIT
 * Reconstructed 42e4a0/42e4f4/42e514/42de0e/42ddf2.
 * Peripheral writes are source-defined semantics, not permission to execute
 * against physical hardware. MRAM routine/platform callbacks remain explicit.
 */
#include "control.h"
extern uint32_t opencfw_boot_control_critical_save(void);
extern uint32_t opencfw_boot_control_guard_begin(void);
extern uint32_t opencfw_boot_control_guard_end(void);
extern uint32_t opencfw_boot_control_mram(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern void opencfw_boot_control_log(uint32_t,uint32_t);
extern void opencfw_boot_control_mode_one(uint32_t);
extern void opencfw_boot_control_mode_two(uint32_t);
extern void opencfw_boot_control_cleanup(void);
static void restore(uint32_t saved) {
    /* Raw M-class instructions unconditionally MSR PRIMASK; the older
     * decompiler's privilege-check narrative is incorrect. */
    __asm__ volatile("msr primask,%0"::"r"(saved):"memory");
}
uint32_t opencfw_boot_mram_aligned(uint32_t key,const void *source,uint32_t destination,uint32_t words) {
    if(destination&3u)return 0x08000140u;
    uint32_t offset=(destination-0x00400000u)>>2;
    uint32_t saved=opencfw_boot_control_critical_save();
    opencfw_boot_control_guard_begin();
    uint32_t result=opencfw_boot_control_mram(key,1,source,offset,words);
    opencfw_boot_control_guard_end();
    restore(saved);
    return result ? result|0x08000100u : 0;
}
uint32_t opencfw_boot_mram_dispatch(uint32_t key,const void *source,uint32_t destination,uint32_t words) {
    if((destination&15u)||(words&3u))return 0x08000140u;
    return opencfw_boot_mram_aligned(key,source,destination,words);
}
uint32_t opencfw_boot_terminal_mode(uint32_t mode) {
    mode&=255u;
    if(mode==0) {
        *(volatile uint32_t *)(uintptr_t)0x40000008u=0xd4u;
        for(;;)__asm__ volatile("":::"memory");
    }
    if(mode==1) {
        *(volatile uint32_t *)(uintptr_t)0x40000004u=0x1bu;
        for(;;)__asm__ volatile("":::"memory");
    }
    return 6;
}
void opencfw_boot_dfu_error_transaction(void) {
    opencfw_boot_control_log(1,0x1f9u);
    uint32_t saved=opencfw_boot_control_critical_save();
    const uint32_t erased_record[4]={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
    (void)opencfw_boot_mram_dispatch(0x12344321u,erased_record,0x007fe000u,4);
    restore(saved);
    (void)opencfw_boot_terminal_mode(0);
}
void opencfw_boot_dfu_runtime_enable(void) {
    (void)opencfw_boot_control_critical_save();
    opencfw_boot_control_mode_one(1);
    opencfw_boot_control_mode_two(1);
    opencfw_boot_control_cleanup();
}
