/* Authenticated CASE standby children 0x08005094/0x080050a8/0x080050c4. */
#include <stdint.h>

uint32_t case_legacy_ee_wake_prepare(uint32_t mode) {
    volatile uint32_t *const gpio=(volatile uint32_t *)(uintptr_t)0x40007000u;
    uint32_t mask=mode&63u;
    gpio[2]=gpio[2]&~mask;
    return mask;
}

uint32_t case_legacy_ee_wake_enable(uint32_t mode) {
    volatile uint32_t *const gpio=(volatile uint32_t *)(uintptr_t)0x40007000u;
    uint32_t mask=mode&63u;
    gpio[3]=(gpio[3]&~mask)|(mode>>8u);
    gpio[2]=gpio[2]|mask;
    return gpio[2];
}

uint32_t case_legacy_ee_enter_standby(void) {
    volatile uint32_t *const gpio=(volatile uint32_t *)(uintptr_t)0x40007000u;
    volatile uint32_t *const scr=(volatile uint32_t *)(uintptr_t)0xe000ed10u;
    gpio[0]=(gpio[0]&~7u)|3u;
    *scr|=4u;
    __asm__ volatile("wfi" ::: "memory");
    return 0xe000ed00u;
}
