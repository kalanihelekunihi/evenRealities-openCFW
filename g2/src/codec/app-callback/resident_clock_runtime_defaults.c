/* SPDX-License-Identifier: MIT
 * Source initializer 0x100268c8..0x10026904. Native clock startup copies this
 * object to the 0x200268c8 runtime alias, then reads/writes words 0, 5, 14.
 * Other fields preserve stock values pending individual consumer attribution.
 */
#include <stdint.h>

struct gx8002_clock_runtime_defaults {
    uint32_t pll_enabled;     /* +0: clock switch/initializer */
    uint32_t words_04_10[4];
    uint32_t pll_target;      /* +0x14: clock initializer */
    uint32_t words_18_34[8];
    uint32_t trim_result;     /* +0x38: clock initializer */
};
_Static_assert(sizeof(struct gx8002_clock_runtime_defaults) == 60,
               "native clock state extent");

const struct gx8002_clock_runtime_defaults gx8002_clock_defaults_268c8
    __attribute__((section(".gx8002.clock_defaults.268c8"), used,
                   aligned(4))) = {
    .pll_enabled = 1u,
    .words_04_10 = {UINT32_C(0x8000), UINT32_C(0x05dc0000),
                    UINT32_C(0x01770000), 0u},
    .pll_target = UINT32_C(0x0bff),
    .words_18_34 = {2u, 0u, 3u, 1u, 0u, 4u, 0u, 0u},
    .trim_result = UINT32_MAX,
};
