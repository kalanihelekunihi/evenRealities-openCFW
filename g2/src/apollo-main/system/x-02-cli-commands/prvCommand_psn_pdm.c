/* Product FreeRTOS-Plus-CLI "AT^psn" and "pdm" commands (two separate
 * stock modules), stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file names not retained). Native: AT^psn 0x58109c..0x5810d7 (inline
 * "%s" 0x5810e4, pool 0x5810e8), pdm 0x5810f0..0x581135 (pool
 * 0x581140..0x58114b). Registrars 0x5810d8 / 0x581136 are in
 * a-59-cli-commands/prvCommand_registrars.c. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define PSN_LENGTH 14u
#define NVDB_SYS_PSN 0u

extern uint32_t g2_log_module_length(const char *text); /* 0x44a43c strlen */
extern int32_t SVC_NvdbWriteSysData(uint32_t item, const char *value); /* 0x4af11c */
extern int32_t string_compare_46cacc(const char *a, const char *b);   /* strcmp */
extern void aud_send_message_type1(uint32_t value);                    /* 0x53ca32 */

static const char s_percent_s[] = "%s"; /* ROM 0x5810e4 */
static const char s_psn_bad[] =
    "AT^psn: set PSN: The parameter is incorrect. Please enter the correct command (len %d)\r\n"; /* ROM 0x6e13d4 */
static const char s_open[] = "open";   /* ROM 0x78e24c */
static const char s_close[] = "close"; /* ROM 0x78e254 */
static const char s_pdm_bad[] =
    "pdm test: The parameter is incorrect. Please enter the correct command\r\n"; /* ROM 0x6f5658 */

int32_t cli_cmd_at_psn_58109c(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_pdm_5810f0(char *write_buffer, size_t write_buffer_len, const char *command_string);

/* "AT^psn <14 chars>": store the product serial number (NV sys item 0). */
int32_t cli_cmd_at_psn_58109c(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *psn;

    (void)write_buffer;
    (void)write_buffer_len;
    psn = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (g2_log_module_length(psn) == PSN_LENGTH) {
        audio_ble_hci_boot_log_4733ee(s_percent_s, psn);
        (void)SVC_NvdbWriteSysData(NVDB_SYS_PSN, psn);
    } else {
        audio_ble_hci_boot_log_4733ee(s_psn_bad, PSN_LENGTH);
    }
    return 0;
}

/* "pdm open|close": audio message type 1 (PDM capture on/off). */
int32_t cli_cmd_pdm_5810f0(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *arg;

    (void)write_buffer;
    (void)write_buffer_len;
    arg = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (string_compare_46cacc(arg, s_open) == 0)
        aud_send_message_type1(1u);
    else if (string_compare_46cacc(arg, s_close) == 0)
        aud_send_message_type1(0u);
    else
        audio_ble_hci_boot_log_4733ee(s_pdm_bad);
    return 0;
}
