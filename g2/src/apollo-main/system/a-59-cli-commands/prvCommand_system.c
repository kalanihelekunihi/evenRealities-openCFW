/* Product FreeRTOS-Plus-CLI system and info commands, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file names not retained; only prvCommand_filesystem.c is named in ROM).
 * Native: reset handler 0x57e3d8..0x57e3e5, system registrar
 * 0x57e626..0x57e665 (pool 0x57e6a4..0x57e6cb), info registrar
 * 0x57e810..0x57e825 (pool 0x57e88c..0x57e897).
 *
 * The other handlers of these modules (clear 0x57e3e6, enterProductMode
 * 0x57e3f4, exitProductMode 0x57e40a, SetGPIO 0x57e420, ResetGPIO 0x57e48e,
 * ProductControlCodec 0x57e4fc, ChargerControl 0x57e55a, ReadDieId
 * 0x57e5b6, ReadChipId 0x57e602, info 0x57e764, AT^thread 0x57e7f6,
 * AT^dump 0x57e800) have no inventory rows and are reached only through
 * the command table. */
#include <stddef.h>
#include <stdint.h>
#include "cli_commands.h"

#define RESET_SWPOR 0u /* am_hal_reset_control: RSTGEN SWPOR (0x40000008 = 0xd4) */

/* Command table rows, initialized SRAM. */
extern g2_cli_command_t g2_cli_cmd_reset_20003338;               /* "reset", 0 params */
extern g2_cli_command_t g2_cli_cmd_clear_20003348;               /* "clear", 0 */
extern g2_cli_command_t g2_cli_cmd_enter_product_mode_20003358;  /* "enterProductMode", 0 */
extern g2_cli_command_t g2_cli_cmd_exit_product_mode_20003368;   /* "exitProductMode", 0 */
extern g2_cli_command_t g2_cli_cmd_set_gpio_20003378;            /* "SetGPIO", 1 */
extern g2_cli_command_t g2_cli_cmd_reset_gpio_20003388;          /* "ResetGPIO", 1 */
extern g2_cli_command_t g2_cli_cmd_product_control_codec_20003398; /* "ProductControlCodec", 1 */
extern g2_cli_command_t g2_cli_cmd_charger_control_200033a8;     /* "ChargerControl", 1 */
extern g2_cli_command_t g2_cli_cmd_read_die_id_200033b8;         /* "ReadDieId", 0 */
extern g2_cli_command_t g2_cli_cmd_read_chip_id_200033c8;        /* "ReadChipId", 0 */
extern g2_cli_command_t g2_cli_cmd_info_200033d8;                /* "info", 0 */
extern g2_cli_command_t g2_cli_cmd_at_thread_200033e8;           /* "AT^thread", 0 */
extern g2_cli_command_t g2_cli_cmd_at_dump_200033f8;             /* "AT^dump", 0 */

extern uint32_t audio_ble_ota_reset_event(uint32_t request, uint32_t unused); /* 0x4d3534 am_hal_reset_control */

int32_t cli_cmd_reset_57e3d8(char *write_buffer, size_t write_buffer_len, const char *command_string);
void cli_register_system_commands_57e626(void);
void cli_register_info_commands_57e810(void);

/* "reset": software power-on reset; does not return in practice. */
int32_t cli_cmd_reset_57e3d8(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    (void)audio_ble_ota_reset_event(RESET_SWPOR, 0u);
    return 0;
}

void cli_register_system_commands_57e626(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_reset_20003338);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_clear_20003348);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_enter_product_mode_20003358);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_exit_product_mode_20003368);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_set_gpio_20003378);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_reset_gpio_20003388);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_product_control_codec_20003398);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_charger_control_200033a8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_read_die_id_200033b8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_read_chip_id_200033c8);
}

void cli_register_info_commands_57e810(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_info_200033d8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_at_thread_200033e8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_at_dump_200033f8);
}
