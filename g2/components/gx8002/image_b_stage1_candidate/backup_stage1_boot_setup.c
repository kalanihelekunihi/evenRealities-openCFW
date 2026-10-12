/* SPDX-License-Identifier: MIT
 * Corrected BINH-B runtime entries: 0x10000df0 boot setup and children.
 * Native read/write order is retained; external children remain real imports.
 */
#include <stdint.h>
#include <spl/spl.h>
extern volatile struct boot_info gx8002_stage1_boot_info;

#define REG32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern void gx8002_image_b_stage1_clock_gate_100001f8(uint32_t, uint32_t);
extern int32_t gx8002_image_b_stage1_loader_10000d4c(void);
extern void gx8002_image_b_stage1_clock_init_100007d8(void);
extern void gx8002_image_b_stage1_timer_config_10001260(uint32_t, uint32_t);

void gx8002_image_b_stage1_audio_gate_10001234(void)
{
    (void)REG32(0xa0500040u);
    REG32(0xa0500030u) = 0;
    REG32(0xa050006cu) = 0;
    (void)REG32(0xa0600040u);
    REG32(0xa0600030u) = 0;
    REG32(0xa060006cu) = 0;
    gx8002_image_b_stage1_clock_gate_100001f8(20u, 0u);
    gx8002_image_b_stage1_clock_gate_100001f8(21u, 0u);
}

void gx8002_image_b_stage1_boot_mode_10000d24(void)
{
    gx8002_image_b_stage1_audio_gate_10001234();
    uint32_t mode = REG32(0xa0010068u) & 15u;
    if (mode == 2u) {
        gx8002_stage1_boot_info.boot_device = (enum boot_device_type)mode;
        gx8002_stage1_boot_info.info.value = REG32(0xa0010068u) & ~255u;
    }
}

uint32_t gx8002_image_b_stage1_clock_status_10000ed0(void)
{
    return REG32(0xa0010030u) & 1u;
}

void gx8002_image_b_stage1_osc_32k_state_10000ea0(uint32_t enabled)
{
    uint32_t value = REG32(0xa0010030u) & ~1u;
    REG32(0xa0010030u) = value;
    REG32(0xa0010030u) = REG32(0xa0010030u) | (enabled & 1u);
}

void gx8002_image_b_stage1_osc_all_state_10000eb8(uint32_t enabled)
{
    uint32_t value = REG32(0xa0010030u) & ~2u;
    REG32(0xa0010030u) = value;
    REG32(0xa0010030u) = REG32(0xa0010030u) | ((enabled << 1) & 2u);
}

void gx8002_image_b_stage1_clock_setup_100012f0(void)
{
    if (gx8002_image_b_stage1_clock_status_10000ed0() == 0u)
        REG32(0xa0010094u) = (REG32(0xa0010094u) & ~15u) | 12u;
}

/* Original 0x10000134 is a return-only leaf. */
void gx8002_image_b_stage1_return_leaf_10000134(void) {}

void gx8002_image_b_stage1_timer_start_100012e0(void)
{
    (void)gx8002_image_b_stage1_timer_config_10001260(0x1c200u, 0u);
}

void gx8002_image_b_stage1_boot_setup_10000df0(void)
{
    gx8002_image_b_stage1_boot_mode_10000d24();
    gx8002_image_b_stage1_clock_setup_100012f0();
    gx8002_image_b_stage1_clock_init_100007d8();
    gx8002_image_b_stage1_return_leaf_10000134();
    gx8002_image_b_stage1_timer_start_100012e0();
    if (gx8002_stage1_boot_info.boot_device == BOOT_DEVICE_NOR)
        (void)gx8002_image_b_stage1_loader_10000d4c();
}
