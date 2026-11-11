/* SPDX-License-Identifier: MIT
 * Bounded reconstruction of locked 0x41acb2..0x41b04b, the bootloader's
 * am_hal_sysctrl_clkmuxrst_low_power_init (called by upstream
 * am_hal_pwrctrl_low_power_init).
 *
 * Stock entered with ambient R1/R2/R5 as the initial GPIO-state bytes, pin
 * configuration and GPIO 15 configuration base. Those carries are zero here:
 * the GPIO-state byte passed to the 32 MHz kick is cleared before use, the pin
 * configuration is read back before it is restored, and the GPIO 15 REFCLK
 * configuration is built from zero with only its function select set (as the
 * upstream sExtRefClkCfg, whose other fields upstream leaves uninitialized).
 */
#include "../platform-control/am_hal_pwrctrl_api.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "apollo510.h"

#define MMIO32(address) (*(volatile uint32_t *)(uintptr_t)(address))

/* Keep each recorded PLL-control write distinct under optimizing compilers. */
__attribute__((noinline)) static void pllctl0_store(uint32_t value)
{
    MCUCTRL->PLLCTL0 = value;
}

_Static_assert(offsetof(STIMER_Type, HALSTATES) == 0x58,
               "Apollo510 HALSTATES address changed");
_Static_assert(offsetof(CLKGEN_Type, CLOCKENSTAT) == 0x30,
               "Apollo510 CLOCKENSTAT address changed");
_Static_assert(offsetof(CLKGEN_Type, MISC) == 0x44,
               "Apollo510 CLKGEN.MISC address changed");
_Static_assert(offsetof(MCUCTRL_Type, PLLCTL0) == 0x4d8,
               "Apollo510 MCUCTRL.PLLCTL0 address changed");
_Static_assert(offsetof(MCUCTRL_Type, PLLMUXCTL) == 0x4e8,
               "Apollo510 MCUCTRL.PLLMUXCTL address changed");

/* Existing native providers / explicit child boundaries. Their bodies are
 * outside this bounded routine and are not claimed as newly reconstructed. */
extern void opencfw_hal_delay_us(uint32_t usec);                         /* 41d1c0 */
extern uint32_t am_hal_delay_us_status_check(uint32_t count, uintptr_t address,
                                        uint32_t mask, uint32_t expected,
                                        uint32_t delay);                  /* 41d246 */
extern uint64_t opencfw_legacy_gpio_mode(uint32_t mode, uint8_t *state);   /* 41d3e4 */
extern uint32_t opencfw_power_register_read(uint32_t id, uint32_t *value); /* 41d90e */
extern uint32_t opencfw_bl_power_register_update(uint32_t id,
                                                  uint32_t value);       /* 41d92c */
extern uint64_t opencfw_low_power_prepare(void);                          /* 41ca5c */
extern uint64_t opencfw_low_power_finish(void);                           /* 41caa2 */
extern uint32_t opencfw_cache_invalidate(const volatile void *range,
                                         uint32_t clean_too);             /* 41e348 */

#include "startup_clockmux.h"

static inline bool flag(uint32_t halstates, unsigned bit)
{
    return (halstates & (UINT32_C(1) << bit)) != 0u;
}

void am_hal_sysctrl_clkmuxrst_low_power_init(void)
{
    uint8_t gpio_state[4] = {0u, 0u, 0u, 0u};
    uint32_t pin_config = 0u;
    uint32_t saved_state;
    uint32_t r5_config;
    unsigned selector;

    saved_state = MMIO32(STIMER_BASE + offsetof(STIMER_Type, HALSTATES));

    /* The second word is read by stock at 0x4000885c, which the public header
     * leaves reserved. Preserve the raw bit test without assigning it meaning. */
    if ((MMIO32(STIMER_BASE + 0x5cu) & 2u) == 0u &&
        (saved_state >> 16) == 0x5af0u) {
        const bool audadc_off = flag(saved_state, 0u);
        const bool hfrc_ded_needed = flag(saved_state, 1u);
        const bool hfrc2_needed = flag(saved_state, 2u);
        const bool xtal_needed = flag(saved_state, 3u);
        const bool extref_needed = flag(saved_state, 4u);
        const bool pll_needed = flag(saved_state, 5u);
        const bool pll_frefsel = flag(saved_state, 6u);
        const bool has_saved_clock = (saved_state & 0x3fu) != 0u;

        if (has_saved_clock) {
            if (audadc_off || hfrc_ded_needed)
                MMIO32(0x400200c0u) |= 1u; /* Reserved in public MCUCTRL map. */

            if (audadc_off) {
                uint32_t value = MCUCTRL->PLLMUXCTL;
                MCUCTRL->PLLMUXCTL = (value & ~0xcu) | 0x4u;
                opencfw_hal_delay_us(1u);
            }

            if (hfrc2_needed) {
                CLKGEN->MISC |= 1u << 5; /* FRCHFRC2 */
                gpio_state[0] = 1u;
                gpio_state[1] = 0u;
                gpio_state[2] = 0u;
                gpio_state[3] = 0u;
                (void)am_hal_delay_us_status_check(200u,
                    (uintptr_t)(CLKGEN_BASE + offsetof(CLKGEN_Type, CLOCKENSTAT)),
                    0x01000000u, 0x01000000u, 1u);
                opencfw_hal_delay_us(5u);
            }

            if (xtal_needed || (pll_needed && !pll_frefsel)) {
                gpio_state[1] = 0u;
                (void)opencfw_legacy_gpio_mode(2u, &gpio_state[1]);
                opencfw_hal_delay_us(1500u);
            }

            if (extref_needed || (pll_needed && pll_frefsel)) {
                /* GPIO 15 function select 10 (REFCLK_EXT). */
                r5_config = 10u;
                (void)opencfw_power_register_read(15u, &pin_config);
                (void)opencfw_bl_power_register_update(15u, r5_config);
            }

            if (pll_needed) {
                (void)opencfw_low_power_prepare();
                /* Preserve the stock pair of separate volatile stores. */
                pllctl0_store(MCUCTRL->PLLCTL0 & ~(1u << 1));
                pllctl0_store(MCUCTRL->PLLCTL0 & ~(1u << 2));
                pllctl0_store((MCUCTRL->PLLCTL0 & ~(1u << 5)) |
                              ((uint32_t)pll_frefsel << 5));
                pllctl0_store(MCUCTRL->PLLCTL0 | (1u << 8));
                pllctl0_store(MCUCTRL->PLLCTL0 | (1u << 29));
            }

            for (selector = 30u; selector <= 33u; ++selector)
                (void)am_hal_pwrctrl_periph_enable(selector);
            (void)am_hal_pwrctrl_periph_enable(26u);
            (void)am_hal_pwrctrl_periph_enable(27u);
            opencfw_hal_delay_us(5u);

            MMIO32(0x40201000u) |= 1u;
            MMIO32(0x40208100u) |= 1u;
            MMIO32(0x40209100u) |= 1u;
            MMIO32(0x400b2000u) &= ~1u; /* Unnamed block in replay headers. */
            MMIO32(0x40210000u) &= ~0x07000000u;
            (void)opencfw_cache_invalidate(NULL, 1u);
            opencfw_hal_delay_us(1u);

            if (audadc_off) {
                uint32_t value = MCUCTRL->PLLMUXCTL;
                MCUCTRL->PLLMUXCTL = (value & ~0xcu) | 0x8u;
            }
            opencfw_hal_delay_us(20u);

            MMIO32(0x40201000u) |= 1u;
            MMIO32(0x40208100u) |= 1u;
            MMIO32(0x40209100u) |= 1u;
            MMIO32(0x400b2000u) &= ~1u;
            for (selector = 30u; selector <= 33u; ++selector)
                (void)am_hal_pwrctrl_periph_disable(selector);
            (void)am_hal_pwrctrl_periph_disable(26u);
            (void)am_hal_pwrctrl_periph_disable(27u);

            if (pll_needed) {
                pllctl0_store(MCUCTRL->PLLCTL0 & ~(1u << 29));
                pllctl0_store(MCUCTRL->PLLCTL0 & ~(1u << 8));
                pllctl0_store(MCUCTRL->PLLCTL0 & ~(1u << 5));
                pllctl0_store(MCUCTRL->PLLCTL0 | (1u << 2));
                pllctl0_store(MCUCTRL->PLLCTL0 | (1u << 1));
                (void)opencfw_low_power_finish();
            }

            if (extref_needed || (pll_needed && pll_frefsel))
                (void)opencfw_bl_power_register_update(15u, pin_config);

            if (xtal_needed || (pll_needed && !pll_frefsel)) {
                gpio_state[0] = 0u;
                (void)opencfw_legacy_gpio_mode(4u, &gpio_state[0]);
            }

            if (hfrc2_needed)
                CLKGEN->MISC &= ~(1u << 5);
            if (audadc_off || hfrc_ded_needed)
                MMIO32(0x400200c0u) &= ~1u;
        }
    }

    /* The stock epilogue resets the marker regardless of guard/body outcome. */
    MMIO32(STIMER_BASE + offsetof(STIMER_Type, HALSTATES)) = 0u;
    MMIO32(STIMER_BASE + offsetof(STIMER_Type, HALSTATES)) =
        (MMIO32(STIMER_BASE + offsetof(STIMER_Type, HALSTATES)) & 0xffffu) |
        0x5af00000u;
}
