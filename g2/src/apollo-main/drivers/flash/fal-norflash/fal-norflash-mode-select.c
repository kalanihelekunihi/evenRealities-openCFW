/* SPDX-License-Identifier: MIT
 * Main 0x46f6ba: shared NOR/MSPI mode byte and 16-byte configuration request.
 * The fixed SRAM configuration block and controller pointer are stock
 * addresses; the transfer at 0x4c0f78 is an independent lower contract.
 */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_mspi_timing_config_20000820[] __asm__("g2_mspi_timing_config_20000820");

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t controller,
                                                     uint32_t count,
                                                     const void *configuration);

void g2_norflash_mode_select_46f6ba(uint32_t mode)
{
    volatile uint8_t *const configuration =
        (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_mspi_timing_config_20000820);
    configuration[5] = (uint8_t)mode == 1u ? 8u : 0u;
    (void)g2_norflash_config_transfer_4c0f78(
        g2_norflash_controller_handle_20074544, 16u,
        (const void *)configuration);
}
