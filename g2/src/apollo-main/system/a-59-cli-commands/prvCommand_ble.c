/* Product FreeRTOS-Plus-CLI BLE commands, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native: hex helpers 0x58143a..0x5814d3,
 * AT^BLERingSend 0x5814d4..0x581551, AT^EM9305 0x581552..0x581563,
 * registrar 0x581644..0x58167d; pool 0x5816f0..0x581773, "\n" at 0x581640.
 *
 * The other handlers (AT^BleGetMac 0x581150, AT^BLECleanBond 0x581180,
 * AT^BLES 0x58118a, AT^BLEM 0x58125e, AT^BLEMC 0x58136c, AT^BLEADV
 * 0x581564, AT^BLE_KEEPCONNECT 0x581628) have no inventory rows.
 *
 * AT^BLERingSend takes one hex string, converts it into a 128-byte stack
 * buffer (stock does not bound the length: more than 256 hex digits
 * overflow it) and sends the bytes to the ring over BLE. */
#include <stddef.h>
#include <stdint.h>
#include "cli_commands.h"

#define RING_SEND_BUFFER_BYTES 128u

extern g2_cli_command_t g2_cli_cmd_ble_get_mac_200030e4;       /* "AT^BleGetMac", 0 params */
extern g2_cli_command_t g2_cli_cmd_ble_clean_bond_200030f4;    /* "AT^BLECleanBond", 0 */
extern g2_cli_command_t g2_cli_cmd_ble_slave_20003104;         /* "AT^BLES", 1 */
extern g2_cli_command_t g2_cli_cmd_ble_master_20003114;        /* "AT^BLEM", 1 */
extern g2_cli_command_t g2_cli_cmd_ble_master_conn_20003124;   /* "AT^BLEMC", 2 */
extern g2_cli_command_t g2_cli_cmd_ble_ring_send_20003134;     /* "AT^BLERingSend", 1 */
extern g2_cli_command_t g2_cli_cmd_em9305_20003144;            /* "AT^EM9305", 0 */
extern g2_cli_command_t g2_cli_cmd_ble_adv_20003154;           /* "AT^BLEADV", 1 */
extern g2_cli_command_t g2_cli_cmd_ble_keep_connect_20003164;  /* "AT^BLE_KEEPCONNECT", 0 */

extern uint32_t g2_log_module_length(const char *text);                   /* 0x44a43c strlen */
extern int32_t iar_isxdigit_595984(int32_t c);
extern int32_t printf_595a34(const char *format, ...);                     /* IAR printf */
extern int32_t iar_strtol_595a2e(const char *s, char **endptr, int32_t base);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *data, uint32_t length); /* APP_BleRingSendDataMsg */
extern void svc_ble_em9305_force_dfu_4b4888(void);

static const char s_odd_length[] = "Error: Input string length must be even.\n";          /* ROM 0x741af8 */
static const char s_bad_digit[] = "Error: Invalid hexadecimal character at position %zu.\n"; /* ROM 0x721940 */
static const char s_ring_send[] = "_BleRingSend %s\r\n";                                 /* ROM 0x7826a0 */
static const char s_hex_byte[] = "%02X ";                                                /* ROM 0x78e01c */
static const char s_newline[] = "\n";                                                    /* ROM 0x581640 */
static const char s_rx_error[] = "rx error\n";                                           /* ROM 0x78b8d0 */
static const char s_ring_bad_param[] =
    "AT^BLERingSend: The parameter is incorrect. Please enter the correct command %s %s\r\n"; /* ROM 0x6e47a0 */
static const char s_force_dfu[] = "_Em9305ForceDfu %s\r\n";                              /* ROM 0x77a93c */

int32_t cli_is_hex_string_58143a(const char *text);
int32_t cli_hex_to_bytes_581462(const char *text, uint8_t *out);
int32_t cli_cmd_ble_ring_send_5814d4(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string);
int32_t cli_cmd_em9305_force_dfu_581552(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string);
void cli_register_ble_commands_581644(void);

/* 1 when every character up to the terminator is a hex digit. */
int32_t cli_is_hex_string_58143a(const char *text)
{
    int32_t length = (int32_t)g2_log_module_length(text);
    int32_t i;

    for (i = 0; i < length; i++) {
        if (iar_isxdigit_595984((uint8_t)text[i]) == 0)
            return 0;
    }
    return 1;
}

/* Two digits per byte via strtol(base 16); errors go to the IAR printf and
 * return -1 (bytes already converted stay in out). */
int32_t cli_hex_to_bytes_581462(const char *text, uint8_t *out)
{
    uint32_t length = g2_log_module_length(text);
    char pair[3];
    char *end;
    uint32_t i;
    int32_t status;

    if ((length & 1u) != 0u) {
        (void)printf_595a34(s_odd_length);
        return -1;
    }
    (void)aeabi_memset_43c0e4(pair, sizeof(pair), 0);
    status = 0;
    for (i = 0u; i < length; i += 2u) {
        int32_t value;

        value = iar_strtol_595a2e((const char *)audio_settings_copy_text(pair, text + i, 2u),
                                  &end, 16);
        if (*end != '\0') {
            (void)printf_595a34(s_bad_digit, i);
            status = -1;
            break;
        }
        out[i >> 1] = (uint8_t)value;
    }
    return status;
}

int32_t cli_cmd_ble_ring_send_5814d4(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string)
{
    int32_t parameter_length = 0;
    uint8_t bytes[RING_SEND_BUFFER_BYTES];
    const char *hex;
    uint32_t count;
    int32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    hex = freertos_cli_get_parameter_5848fc(command_string, 1u, &parameter_length);
    if (cli_is_hex_string_58143a(hex) == 0) {
        audio_ble_hci_boot_log_4733ee(s_ring_bad_param, command_string, hex);
        return 0;
    }
    audio_ble_hci_boot_log_4733ee(s_ring_send, hex);
    count = g2_log_module_length(hex) >> 1;
    if (cli_hex_to_bytes_581462(hex, bytes) != 0) {
        audio_ble_hci_boot_log_4733ee(s_rx_error);
        return 0;
    }
    for (i = 0; i < (int32_t)count; i++)
        audio_ble_hci_boot_log_4733ee(s_hex_byte, bytes[i]);
    audio_ble_hci_boot_log_4733ee(s_newline);
    (void)audio_uart_ring_ble_send_data_4c4b7e(bytes, (uint16_t)count);
    return 0;
}

/* "AT^EM9305": force the EM9305 radio into DFU and reflash it. */
int32_t cli_cmd_em9305_force_dfu_581552(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    audio_ble_hci_boot_log_4733ee(s_force_dfu, command_string);
    svc_ble_em9305_force_dfu_4b4888();
    return 0;
}

void cli_register_ble_commands_581644(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_get_mac_200030e4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_clean_bond_200030f4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_slave_20003104);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_master_20003114);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_master_conn_20003124);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_ring_send_20003134);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_em9305_20003144);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_adv_20003154);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ble_keep_connect_20003164);
}
