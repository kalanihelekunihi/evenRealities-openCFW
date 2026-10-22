/* Product FreeRTOS-Plus-CLI log commands "logcat", "logf" and
 * "AT^LOGTYPE", stock directory D:\01_workspace\s200_ap510b_iar_git\
 * kernel\FreeRTOS-Plus-CLI\prvCommand\ (file name not retained). Native:
 * logcat 0x580430..0x5804bf, logf 0x5804c0..0x5804ff, inline flags
 * 0x580500..0x580517, AT^LOGTYPE 0x580518..0x5807bb, inline strings
 * 0x5807bc..0x5807bf and 0x5807d8..0x5807f3, pool 0x5807f4..0x580817.
 * The registrar 0x5807c0 is in a-59-cli-commands/prvCommand_registrars.c.
 *
 * Level flags map to EasyLogger levels: -a 0 (assert) .. -v 5 (verbose).
 * AT^LOGTYPE <STORE_UART|UART|STORE|BLE> <flag> selects the compressed-log
 * output (bit 0 store, bit 1 UART, bit 2 BLE) and sets the compressed-log
 * level; STORE_UART and UART also set the EasyLogger filter level. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define LOG_OUT_STORE 1u
#define LOG_OUT_UART 2u
#define LOG_OUT_STORE_UART 3u
#define LOG_OUT_BLE 4u

extern int32_t string_compare_46cacc(const char *a, const char *b); /* strcmp */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern void elog_set_filter_lvl_43d3a6(uint8_t level);
extern void elog_set_filter_tag_43d406(const char *tag); /* strncpy 30 bytes into the elog filter */
extern void compress_log_set_output_flags_43d0c8(uint8_t flags);
extern void audio_log_policy_set_43d0d4(uint8_t level); /* compressed-log level, RAM 0x20004544 */

/* logcat flags, ROM 0x580500.. ; AT^LOGTYPE uses identical copies at 0x5807d8.. */
static const char s_flag_v[] = "-v"; /* ROM 0x580500 / 0x5807d8 */
static const char s_flag_d[] = "-d"; /* ROM 0x580504 / 0x5807dc */
static const char s_flag_i[] = "-i"; /* ROM 0x580508 / 0x5807e0 */
static const char s_flag_w[] = "-w"; /* ROM 0x58050c / 0x5807e4 */
static const char s_flag_e[] = "-e"; /* ROM 0x580510 / 0x5807e8 */
static const char s_flag_a[] = "-a"; /* ROM 0x580514 / 0x5807ec */
static const char s_null[] = "null";  /* ROM 0x78e1fc */
static const char s_null_upper[] = "NULL"; /* ROM 0x78e204 */
static const char s_empty[] = "";     /* ROM 0x5807bc */
static const char s_store_uart[] = "STORE_UART"; /* ROM 0x78b9a8 */
static const char s_store_uart_log[] = "Compress log type set to STORE_UART\r\n"; /* ROM 0x74ce54 */
static const char s_uart[] = "UART";  /* ROM 0x78e20c */
static const char s_uart_log[] = "log type set to UART\r\n"; /* ROM 0x77aaec */
static const char s_store[] = "STORE"; /* ROM 0x78e214 */
static const char s_store_log[] = "Compress log type set to STORE\r\n"; /* ROM 0x758604 */
static const char s_ble[] = "BLE";    /* ROM 0x5807f0 */
static const char s_ble_log[] = "Compress log type set to BLE\r\n"; /* ROM 0x763e90 */

int32_t cli_cmd_logcat_580430(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_logf_5804c0(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_at_logtype_580518(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string);

/* "-v".."-a" -> 5..0, anything else -> -1 (ignored). */
static int32_t log_flag_level(const char *flag)
{
    if (string_compare_46cacc(flag, s_flag_v) == 0)
        return 5;
    if (string_compare_46cacc(flag, s_flag_d) == 0)
        return 4;
    if (string_compare_46cacc(flag, s_flag_i) == 0)
        return 3;
    if (string_compare_46cacc(flag, s_flag_w) == 0)
        return 2;
    if (string_compare_46cacc(flag, s_flag_e) == 0)
        return 1;
    if (string_compare_46cacc(flag, s_flag_a) == 0)
        return 0;
    return -1;
}

/* "logcat <flag>": EasyLogger output level. */
int32_t cli_cmd_logcat_580430(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    const char *flag;
    int32_t level;

    (void)write_buffer;
    (void)write_buffer_len;
    flag = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (flag == NULL)
        return 0;
    level = log_flag_level(flag);
    if (level >= 0)
        elog_set_filter_lvl_43d3a6((uint8_t)level);
    return 0;
}

/* "logf <tag>": EasyLogger tag filter; "null"/"NULL" clears it. */
int32_t cli_cmd_logf_5804c0(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    const char *tag;

    (void)write_buffer;
    (void)write_buffer_len;
    tag = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (tag == NULL)
        return 0;
    if (string_compare_46cacc(tag, s_null) == 0 || string_compare_46cacc(tag, s_null_upper) == 0)
        elog_set_filter_tag_43d406(s_empty);
    else
        elog_set_filter_tag_43d406(tag);
    return 0;
}

int32_t cli_cmd_at_logtype_580518(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string)
{
    int32_t length = 0;
    const char *type;
    const char *flag;
    int32_t level;

    (void)write_buffer;
    (void)write_buffer_len;
    type = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    flag = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    if (type == NULL || flag == NULL)
        return 0;
    if (audio_ble_hci_vendor_compare_44b610(type, s_store_uart, 10u) == 0) {
        compress_log_set_output_flags_43d0c8(LOG_OUT_STORE_UART);
        audio_ble_hci_boot_log_4733ee(s_store_uart_log);
        level = log_flag_level(flag);
        if (level >= 0) {
            audio_log_policy_set_43d0d4((uint8_t)level);
            elog_set_filter_lvl_43d3a6((uint8_t)level);
        }
    } else if (audio_ble_hci_vendor_compare_44b610(type, s_uart, 4u) == 0) {
        compress_log_set_output_flags_43d0c8(LOG_OUT_UART);
        audio_ble_hci_boot_log_4733ee(s_uart_log);
        level = log_flag_level(flag);
        if (level >= 0)
            elog_set_filter_lvl_43d3a6((uint8_t)level);
    } else if (audio_ble_hci_vendor_compare_44b610(type, s_store, 5u) == 0) {
        compress_log_set_output_flags_43d0c8(LOG_OUT_STORE);
        audio_ble_hci_boot_log_4733ee(s_store_log);
        level = log_flag_level(flag);
        if (level >= 0)
            audio_log_policy_set_43d0d4((uint8_t)level);
    } else if (audio_ble_hci_vendor_compare_44b610(type, s_ble, 3u) == 0) {
        compress_log_set_output_flags_43d0c8(LOG_OUT_BLE);
        audio_ble_hci_boot_log_4733ee(s_ble_log);
        level = log_flag_level(flag);
        if (level >= 0)
            audio_log_policy_set_43d0d4((uint8_t)level);
    }
    return 0;
}
