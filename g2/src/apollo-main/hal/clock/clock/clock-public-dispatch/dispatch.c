#include "dispatch.h"
#include "../clock-manager-ownership/ownership.h"
#include "../../xtal-request/request.h"
#include "../../hfrc-syspll/clocks.h"
#include "../clock-leaf-providers/providers.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");
extern uint32_t stock_save_irq(void);
static void restore_irq(uint32_t saved) {
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
}
static uint32_t ownership(uint32_t clock, uint32_t user, uint32_t requested) {
    user = (uint8_t)user;
    if (audio_clock_user(clock, user) == requested) return 0;
    uint32_t saved = stock_save_irq();
    /* Stock children discard setter status; public dispatch validates user. */
    (void)audio_clock_set(clock, user, requested);
    restore_irq(saved);
    return 0;
}
uint32_t audio_lfrc_request(uint32_t user) { return ownership(0, user, 1); }
uint32_t audio_lfrc_release(uint32_t user) { return ownership(0, user, 0); }
uint32_t audio_xtal_ls_request(uint32_t user) {
    if (!*(volatile uint32_t *)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x10u)) return 7;
    /* No stock EXT32K enable/status path: SDK optional code was compiled out. */
    return ownership(1, user, 1);
}
uint32_t audio_xtal_ls_release(uint32_t user) { return ownership(1, user, 0); }
uint32_t audio_clock_request(uint32_t clock, uint32_t user) {
    clock = (uint8_t)clock;
    user = (uint8_t)user;
    if (user >= 57) return 6;
    switch (clock) {
    case 0: return audio_lfrc_request(user);
    case 1: return audio_xtal_ls_request(user);
    case 2: return audio_xtal_request(user);
    case 3: return audio_ext_request(user);
    case 4: return audio_hfrc_request(user);
    case 5: return audio_hfrc2_request(user);
    case 6: return audio_syspll_request(user);
    default: return 6;
    }
}
uint32_t audio_clock_release(uint32_t clock, uint32_t user) {
    clock = (uint8_t)clock;
    user = (uint8_t)user;
    if (user >= 57) return 6;
    switch (clock) {
    case 0: return audio_lfrc_release(user);
    case 1: return audio_xtal_ls_release(user);
    case 2: return audio_xtal_release(user);
    case 3: return audio_ext_release(user);
    case 4: return audio_hfrc_release(user);
    case 5: return audio_hfrc2_release(user);
    case 6: return audio_syspll_release(user);
    default: return 6;
    }
}
