/* SPDX-License-Identifier: MIT
 * Main 0x470d7c: NOR/MSPI serial-mode reconfiguration sequence.
 * Disable/configure/enable and final clock selection are hardware lowers.
 */
#include <stdint.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern uint32_t g2_norflash_disable_mspi_4c0ea8(uint32_t controller);
extern uint32_t g2_norflash_configure_mspi_4c099c(uint32_t controller,
                                                    const void *configuration);
extern uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t controller);
extern void g2_norflash_clock_select_4c32b4(uint32_t clock_handle,
                                              uint32_t mode);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char function[] = "am_devices_mspi_device_reconfigure";
static const char disable_error[] = "Error - Failed to disable mspi.\n";
static const char disable_error_short[] =
    "[drv.norflash]Error - Failed to disable mspi.\n";
static const char configure_error[] = "Error - Failed to configure mspi.\n";
static const char configure_error_short[] =
    "[drv.norflash]Error - Failed to configure mspi.\n";

static void report(uint32_t line, const char *message,
                   const char *short_message)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(2u, module, file, function, line, message);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x08000000u, short_message, short_message);
}

uint32_t g2_norflash_set_serial_470d7c(const void *configuration)
{
    uint32_t controller = g2_norflash_controller_handle_20074544;
    if (g2_norflash_disable_mspi_4c0ea8(controller) != 0u) {
        report(1418u, disable_error, disable_error_short);
        return 1u;
    }
    controller = g2_norflash_controller_handle_20074544;
    if (g2_norflash_configure_mspi_4c099c(controller, configuration) != 0u) {
        report(1426u, configure_error, configure_error_short);
        return 1u;
    }
    controller = g2_norflash_controller_handle_20074544;
    if (g2_norflash_enable_mspi_4c0e1e(controller) != 0u) {
        report(1434u, configure_error, configure_error_short);
        return 1u;
    }
    uint32_t clock_context = *(volatile uint32_t *)(uintptr_t)0x20074540u;
    uint32_t clock_handle = *(volatile uint32_t *)(uintptr_t)clock_context;
    uint32_t mode = ((const uint8_t *)configuration)[8];
    g2_norflash_clock_select_4c32b4(clock_handle, mode);
    return 0u;
}
