/* Product FreeRTOS-Plus-CLI command modules (stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\),
 * shared declarations for the a-59 command units.
 *
 * Every command definition is a 16-byte CLI_Command_Definition_t in
 * initialized SRAM (decoded from the 0x20000000 init stream, record
 * 0x75d3f4); each module registers its rows with
 * FreeRTOS_CLIRegisterCommand. Handlers write their output with the
 * console printf at 0x4733ee, never to the write buffer, and return 0
 * (pdFALSE: no more output). */
#ifndef G2_A59_CLI_COMMANDS_H
#define G2_A59_CLI_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

/* pdCOMMAND_LINE_CALLBACK */
typedef int32_t (*g2_cli_callback_t)(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string);

/* CLI_Command_Definition_t */
typedef struct {
    const char *command;            /* +0x0 */
    const char *help;               /* +0x4 */
    g2_cli_callback_t interpreter;  /* +0x8 */
    int8_t expected_parameters;     /* +0xc, -1 = variable */
} g2_cli_command_t;
_Static_assert(sizeof(g2_cli_command_t) == 16u, "CLI_Command_Definition_t is 16 bytes");

/* FreeRTOS-Plus-CLI (upstream FreeRTOS_CLI.c). */
extern int32_t freertos_cli_register_command_5847ac(const g2_cli_command_t *command); /* FreeRTOS_CLIRegisterCommand */
extern const char *freertos_cli_get_parameter_5848fc(const char *command, uint32_t index,
                                                     int32_t *length); /* FreeRTOS_CLIGetParameter */

/* Console printf (UART shell). */
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...);

#endif
