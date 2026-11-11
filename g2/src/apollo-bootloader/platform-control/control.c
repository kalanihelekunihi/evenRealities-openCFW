/* SPDX-License-Identifier: MIT
 * Reconstructed 42e4a0/42e4f4/42e514/42de0e/42ddf2.
 * Peripheral writes are source-defined semantics, not permission to execute
 * against physical hardware. MRAM routine/platform callbacks remain explicit.
 */
#include "control.h"
extern uint32_t am_hal_interrupt_master_disable(void);
#include "am_hal_pwrctrl_api.h"
extern uint32_t opencfw_boot_control_mram(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern void opencfw_boot_control_log(uint32_t,uint32_t);
extern void opencfw_boot_control_mode_one(uint32_t);
static void restore(uint32_t saved) {
    /* Raw M-class instructions unconditionally MSR PRIMASK; the older
     * decompiler's privilege-check narrative is incorrect. */
    __asm__ volatile("msr primask,%0"::"r"(saved):"memory");
}
/* Stock 0x42e4a0 (aligned_guarded_dispatch_42e4a0) */
uint32_t opencfw_boot_mram_aligned(uint32_t key,const void *source,uint32_t destination,uint32_t words) {
    if(destination&3u)return 0x08000140u;
    uint32_t offset=(destination-0x00400000u)>>2;
    uint32_t saved=am_hal_interrupt_master_disable();
    (void)am_hal_pwrctrl_rom_enable();
    uint32_t result=opencfw_boot_control_mram(key,1,source,offset,words);
    (void)am_hal_pwrctrl_rom_disable();
    restore(saved);
    return result ? result|0x08000100u : 0;
}
/* Stock 0x42e4f4 (alignment_dispatch_42e4f4) */
uint32_t opencfw_boot_mram_dispatch(uint32_t key,const void *source,uint32_t destination,uint32_t words) {
    if((destination&15u)||(words&3u))return 0x08000140u;
    return opencfw_boot_mram_aligned(key,source,destination,words);
}
/* Stock 0x42e514 (terminal_mode_42e514) */
uint32_t opencfw_boot_terminal_mode(uint32_t mode) {
    mode&=255u;
    if(mode==0) {
        *(volatile uint32_t *)(uintptr_t)0x40000008u=0xd4u;
        for(;;){ }
    }
    if(mode==1) {
        *(volatile uint32_t *)(uintptr_t)0x40000004u=0x1bu;
        for(;;){ }
    }
    return 6;
}
/* Stock 0x42de0e (critical_dispatch_transaction_42de0e) */
void opencfw_boot_dfu_error_transaction(void) {
    opencfw_boot_control_log(1,0x1f9u);
    uint32_t saved=am_hal_interrupt_master_disable();
    const uint32_t erased_record[4]={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
    (void)opencfw_boot_mram_dispatch(0x12344321u,erased_record,0x007fe000u,4);
    restore(saved);
    (void)opencfw_boot_terminal_mode(0);
}
/* Stock 0x42ddf2 (runtime_enable_sequence_42ddf2) */
void opencfw_boot_dfu_runtime_enable(void) {
    (void)am_hal_interrupt_master_disable();
    opencfw_boot_control_mode_one(1);
    (void)am_hal_pwrctrl_mcu_mode_select(1);
    (void)am_hal_pwrctrl_settings_restore();
}
