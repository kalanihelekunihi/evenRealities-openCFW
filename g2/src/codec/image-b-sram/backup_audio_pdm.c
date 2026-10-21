/* SPDX-License-Identifier: MIT
 * Image-B PDM input setup 0x10005394; native writes precede the 10 ms delay.
 */
#include <stdint.h>

#define PDM_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define PDM_STATE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017624))

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);
extern void gx8002_image_b_delay_ms_10005194(uint32_t milliseconds);

uint32_t gx8002_image_b_pdm_input_10005394(uint32_t clock_mode)
{
    gx8002_image_b_platform_gate_10003be8(8u, 1u);
    PDM_WORD(0x28u) = PDM_WORD(0x28u) & ~UINT32_C(0xfc00);
    PDM_WORD(0x2cu) = PDM_WORD(0x2cu) & ~UINT32_C(0xfc00);
    PDM_WORD(0u) = (PDM_WORD(0u) & ~(1u << 9)) |
                   ((clock_mode & 1u) << 9);
    PDM_WORD(0u) = PDM_WORD(0u) | (1u << 14);
    PDM_STATE = PDM_STATE | 2u;
    gx8002_image_b_delay_ms_10005194(10u);
    return 0u;
}
