/* SPDX-License-Identifier: MIT
 * Main 0x470f68/0x470e90 NOR serial/quad mode wrappers. The mode validator
 * and 24-bit configuration transfer are separate lower contracts.
 */
#include <stdint.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern uint32_t g2_norflash_set_serial_470d7c(const void *configuration);
extern void g2_norflash_mode_select_46f6ba(uint32_t mode);
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t controller,
                                                     uint32_t command,
                                                     const void *payload);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* 0x439c04 */
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "drv.norflash";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char serial_function[] = "mx25u25643g_set_serail_mode";
static const char quad_function[] = "mx25u25643g_set_quad_mode";
static const char serial_reconfigure[] = "Failed to reconfigure serail mode\n";
static const char serial_reconfigure_short[] =
    "[drv.norflash]Failed to reconfigure serail mode\n";
static const char serial_control[] = "Failed to control serail mode\n";
static const char serial_control_short[] =
    "[drv.norflash]Failed to control serail mode\n";
static const char quad_reconfigure[] = "Failed to reconfigure quad mode\n";
static const char quad_reconfigure_short[] =
    "[drv.norflash]Failed to reconfigure quad mode\n";
static const char quad_control[] = "Failed to control quad mode\n";
static const char quad_control_short[] =
    "[drv.norflash]Failed to control quad mode\n";

static void report(uint32_t line, const char *function,
                   const char *message, const char *short_message)
{
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(2u, module, file, function, line, message);
    if (g2_flashdb_candidate_flags() & 1u ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x08000000u, short_message, short_message);
}

void g2_norflash_enter_470f68(void)
{
    const void *const serial_configuration = (const void *)(uintptr_t)0x200007f0u;
    if (g2_norflash_set_serial_470d7c(serial_configuration) != 0u) {
        report(1472u, serial_function, serial_reconfigure,
               serial_reconfigure_short);
        return;
    }
    g2_norflash_mode_select_46f6ba(0u);
    uint8_t control = 0u;
    if (g2_norflash_config_transfer_4c0f78(
            g2_norflash_controller_handle_20074544, 24u,
            &control) != 0u)
        report(1479u, serial_function, serial_control,
               serial_control_short);
}

void g2_norflash_exit_470e90(void)
{
    uint8_t configuration[24];
    audio_uart_checksum_copy(configuration,
                             (const void *)(uintptr_t)0x20000808u, 24u);
    configuration[8] = 16u;
    configuration[4] = 108u;
    configuration[5] = 0u;
    configuration[0] = 8u;
    configuration[15] = 1u;
    if (g2_norflash_set_serial_470d7c(configuration) != 0u) {
        report(1454u, quad_function, quad_reconfigure,
               quad_reconfigure_short);
        return;
    }
    g2_norflash_mode_select_46f6ba(1u);
    uint8_t control = 16u;
    if (g2_norflash_config_transfer_4c0f78(
            g2_norflash_controller_handle_20074544, 24u,
            &control) != 0u)
        report(1461u, quad_function, quad_control,
               quad_control_short);
}
