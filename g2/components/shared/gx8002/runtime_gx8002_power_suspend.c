/* SPDX-License-Identifier: MIT */
/* Recovered LvpPmuSuspend, pinned upstream lvp_pmu.c lineage. */
#include "runtime_gx8002_power_registration.h"
extern unsigned gx_lock_irq_save(void);
extern void gx_unlock_irq_restore(unsigned);
extern void gx_disable_all_interrupt(void);
extern void open_cfw_gx8002_audio_input_suspend(void);
extern int gx_snpu_get_state(void);
extern int gx_snpu_exit(void);
extern int gx_pmu_ctrl_set(unsigned, void *);
extern int gx_pmu_ctrl_enable(void);
extern int gx_audio_in_set_interrupt_enable(unsigned, unsigned);
extern int printf(const char *, ...);
const char open_cfw_gx8002_power_sleep_message[]
    __attribute__((section(".rodata.sleep_message"),aligned(1))) = "set mcu sleep\n";
int open_cfw_gx8002_power_suspend(int type)
{
    struct open_cfw_gx8002_power_state *state = &open_cfw_gx8002_power_state;
    /* Keep the shared-state base in a compact-addressing register. */
    __asm__("" : "+a"(state));
    state = __builtin_assume_aligned(state, 4);
    unsigned irq = gx_lock_irq_save();
    /* The first state word is the active suspend-lock mask. */
    uint32_t active_locks;
    __builtin_memcpy(&active_locks, state->unrecovered_header, sizeof active_locks);
    if (active_locks) {
        gx_unlock_irq_restore(irq);
        return -1;
    }
    for (unsigned i = 0; i < state->suspend_count; ++i) {
        struct open_cfw_app_power_registration *entry = &state->suspend[i];
        entry->callback(entry->private_data);
    }
    gx_unlock_irq_restore(irq);
    open_cfw_gx8002_audio_input_suspend();
    while (gx_snpu_get_state() == 1) { }
    gx_snpu_exit();
    struct { uint8_t from; uint32_t address; } wakeup;
    wakeup.from = 1;
    wakeup.address = 0x10023500;
    int data = type;
    gx_pmu_ctrl_set(3, &data);
    gx_pmu_ctrl_set(5, &wakeup);
    gx_disable_all_interrupt();
    if (data & 4) gx_audio_in_set_interrupt_enable(0x10000, 1);
    printf(open_cfw_gx8002_power_sleep_message);
    gx_pmu_ctrl_enable();
    return 0;
}
