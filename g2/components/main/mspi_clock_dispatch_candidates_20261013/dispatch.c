/* SPDX-License-Identifier: MIT
 * Main 0x4c44bc/0x4c4530: clock provider dispatch by class and peripheral.
 * The selected per-class providers remain explicit link dependencies.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_acquire_0_4c3bfc(uint32_t);
extern uint32_t g2_main_clock_acquire_1_4c3c60(uint32_t);
extern uint32_t g2_main_clock_acquire_2_4c3d9e(uint32_t);
extern uint32_t g2_main_clock_acquire_3_4c3cd4(uint32_t);
extern uint32_t g2_main_clock_acquire_4_4c3f2a(uint32_t);
extern uint32_t g2_main_clock_acquire_5_4c4086(uint32_t);
extern uint32_t g2_main_clock_acquire_6_4c427e(uint32_t);

extern uint32_t g2_main_clock_release_0_4c3c2e(uint32_t);
extern uint32_t g2_main_clock_release_1_4c3ca2(uint32_t);
extern uint32_t g2_main_clock_release_2_4c3e9a(uint32_t);
extern uint32_t g2_main_clock_release_3_4c3d28(uint32_t);
extern uint32_t g2_main_clock_release_4_4c4016(uint32_t);
extern uint32_t g2_main_clock_release_5_4c420c(uint32_t);
extern uint32_t g2_main_clock_release_6_4c43ec(uint32_t);

uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t clock_class,
                                              uint32_t peripheral)
{
    const uint8_t cls = (uint8_t)clock_class;
    const uint8_t id = (uint8_t)peripheral;
    if (id >= 0x39u) return 6u;
    switch (cls) {
    case 0: return g2_main_clock_acquire_0_4c3bfc(id);
    case 1: return g2_main_clock_acquire_1_4c3c60(id);
    case 2: return g2_main_clock_acquire_2_4c3d9e(id);
    case 3: return g2_main_clock_acquire_3_4c3cd4(id);
    case 4: return g2_main_clock_acquire_4_4c3f2a(id);
    case 5: return g2_main_clock_acquire_5_4c4086(id);
    case 6: return g2_main_clock_acquire_6_4c427e(id);
    default: return 6u;
    }
}

uint32_t g2_main_mspi_clock_release_4c4530(uint32_t clock_class,
                                              uint32_t peripheral)
{
    const uint8_t cls = (uint8_t)clock_class;
    const uint8_t id = (uint8_t)peripheral;
    if (id >= 0x39u) return 6u;
    switch (cls) {
    case 0: return g2_main_clock_release_0_4c3c2e(id);
    case 1: return g2_main_clock_release_1_4c3ca2(id);
    case 2: return g2_main_clock_release_2_4c3e9a(id);
    case 3: return g2_main_clock_release_3_4c3d28(id);
    case 4: return g2_main_clock_release_4_4c4016(id);
    case 5: return g2_main_clock_release_5_4c420c(id);
    case 6: return g2_main_clock_release_6_4c43ec(id);
    default: return 6u;
    }
}
