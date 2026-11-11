/* SPDX-License-Identifier: MIT
 * BINH A stage-1 boot-mode, oscillator status, and timer setup leaves.
 * MMIO order and call targets follow the locked C-SKY boot block.
 */
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern void gx8002_image_a_stage1_clock_gate_100005a4(uint32_t, uint32_t);
extern void gx8002_image_a_stage1_timer_config_10000e84(uint32_t, uint32_t);

__attribute__((used, section(".spl_a.audio_gate")))
void gx8002_image_a_stage1_audio_gate_10000e58(void)
{
    (void)REG32(UINT32_C(0xa0500040));
    REG32(UINT32_C(0xa0500030)) = 0u;
    REG32(UINT32_C(0xa050006c)) = 0u;
    (void)REG32(UINT32_C(0xa0600040));
    REG32(UINT32_C(0xa0600030)) = 0u;
    REG32(UINT32_C(0xa060006c)) = 0u;
    gx8002_image_a_stage1_clock_gate_100005a4(20u, 0u);
    gx8002_image_a_stage1_clock_gate_100005a4(21u, 0u);
}

__attribute__((used, section(".spl_a.boot_mode")))
void gx8002_image_a_stage1_boot_mode_10000a04(void)
{
    gx8002_image_a_stage1_audio_gate_10000e58();
    uint32_t mode = REG32(UINT32_C(0xa0010068)) & 15u;
    if (mode == 2u) {
        volatile uint32_t *boot_info;
        __asm__ volatile ("lrw %0, 0x20001280" : "=r"(boot_info));
        boot_info[0] = mode;
        boot_info[1] = REG32(UINT32_C(0xa0010068)) & ~UINT32_C(0xff);
    }
}

__attribute__((noinline, used, section(".spl_a.clock_status")))
uint32_t gx8002_image_a_stage1_clock_status_10000b40(void)
{
    return REG32(UINT32_C(0xa0010030)) & 1u;
}

__attribute__((noinline, used, section(".spl_a.osc_all_state")))
void gx8002_image_a_stage1_osc_all_state_10000b28(uint32_t enabled)
{
    REG32(UINT32_C(0xa0010030)) &= ~2u;
    REG32(UINT32_C(0xa0010030)) |= (enabled << 1) & 2u;
}

__attribute__((noinline, used, section(".spl_a.osc_32k_state")))
void gx8002_image_a_stage1_osc_32k_state_10000b10(uint32_t enabled)
{
    REG32(UINT32_C(0xa0010030)) &= ~1u;
    REG32(UINT32_C(0xa0010030)) |= enabled & 1u;
}

__attribute__((used, section(".spl_a.clock_setup")))
void gx8002_image_a_stage1_clock_setup_10000f14(void)
{
    if (gx8002_image_a_stage1_clock_status_10000b40() == 0u)
        REG32(UINT32_C(0xa0010094)) =
            (REG32(UINT32_C(0xa0010094)) & ~15u) | 12u;
}

__attribute__((used, section(".spl_a.timer_start")))
void gx8002_image_a_stage1_timer_start_10000f04(uint32_t mode,
                                                  uint32_t reserved)
{
    (void)mode;
    (void)reserved;
    gx8002_image_a_stage1_timer_config_10000e84(UINT32_C(0x1c200), 0u);
}
