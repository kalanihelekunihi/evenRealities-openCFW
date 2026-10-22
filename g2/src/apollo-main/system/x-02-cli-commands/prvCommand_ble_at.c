/* Product FreeRTOS-Plus-CLI BLE AT commands, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native: AT^BleGetMac 0x581150..0x58117f,
 * AT^BLECleanBond 0x581180..0x581189, AT^BLES 0x58118a..0x58125d,
 * AT^BLEM 0x58125e..0x5812e9, MAC helpers 0x5812ea..0x58136b, AT^BLEMC
 * 0x58136c..0x581439, AT^BLEADV 0x581564..0x581627, AT^BLE_KEEPCONNECT
 * 0x581628..0x58163d; pool 0x581680..0x58174f, "\n" at 0x581640.
 * The hex helpers, AT^BLERingSend, AT^EM9305 and the registrar of the
 * same stock module are in a-59-cli-commands/prvCommand_ble.c. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define BLE_MAC_TEXT_LENGTH 17u /* "XX:XX:XX:XX:XX:XX" */
#define BLE_MAC_BYTES 6u
#define BLE_SCAN_START 4u
#define BLE_SCAN_STOP 0x20u
#define BLE_MASTER_CONNECT 1u
#define BLE_MASTER_DISCONNECT 0x102u
#define BLE_KEEP_CONNECT_FLAG 0x80u
#define BLE_ADV_IDLE 0u
#define BLE_ADV_ADVERTISING 1u
#define BLE_ADV_STARTING 3u
#define BLE_ADV_STOPPING 5u

extern int32_t string_compare_46cacc(const char *a, const char *b); /* strcmp */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern uint32_t g2_log_module_length(const char *text);  /* 0x44a43c strlen */
extern int32_t iar_isxdigit_595984(int32_t c);
extern int32_t iar_strtol_595a2e(const char *s, char **endptr, int32_t base);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern const uint8_t *APP_BleAddressGet(void); /* 0x4b80ea */
extern const char *APP_BleNameGet(void);       /* 0x46ed08 */
extern void app_clear_all_bonding_info_4b46ce(void);
extern void audio_ble_app_adv_set_state(uint8_t); /* 0x4b467c AppSetBondable */
extern uint8_t audio_ble_app_adv_state(void);     /* 0x4b46a8 */
extern void AppAdvStart(uint8_t mode);            /* 0x4b2d22 */
extern void APP_BleSlaveDisconnect(void);         /* 0x46f0ec, stock passes r0 = 0 */
extern void ble_hci_radio_reset_4b4dc4(void);     /* radio shutdown + boot + DmDevReset */
extern void ble_appdb_print_all_47ca9c(void);
extern void app_ble_hw_error_reset_4b8224(void);  /* "APP_BleHwErrorReset" */
extern void APP_MasterScanEvent(uint8_t state);   /* 0x4a21cc */
extern uint32_t audio_ble_master_is_connected_4a22c6(void);
extern void APP_MasterSetTargetAddrName(const uint8_t *address, const char *name,
                                        uint8_t name_length); /* 0x4a2068 */
extern void APP_MasterConnectEvent(uint32_t event); /* 0x4a1b60 */
extern void audio_ble_phone_advertising_restart(void); /* APP_BleSlaveAdvStartEvent 0x46ee70 */
extern void APP_BleSlaveAdvStopEvent(void);            /* 0x46eeec */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                       uint32_t delay_ms); /* 0x47697e */
extern uint8_t audio_ble_dm_adv_state(uint8_t handle); /* 0x4bac4e */
extern void slave_adv_stop_flag_or_0046f2dc(uint8_t flag);

static const char s_get_mac[] =
    "BLE NAME:[%s]\r\n#BLE addr [%02X:%02X:%02X:%02X:%02X:%02X]"; /* ROM 0x717b90 */
static const char s_bondable[] = "Bondable";               /* ROM 0x78b864 */
static const char s_bondable_log[] = "AppSetBondable true\r\n";  /* ROM 0x77a8dc */
static const char s_disbondable[] = "Disbondable";         /* ROM 0x78b870 */
static const char s_disbondable_log[] = "AppSetBondable false\r\n"; /* ROM 0x77a8f4 */
static const char s_disconn[] = "DISCONN";                 /* ROM 0x78dff4 */
static const char s_disconn_log[] = "Slave disconnect\r\n";  /* ROM 0x782678 */
static const char s_reset9305[] = "RESET9305";             /* ROM 0x78b87c */
static const char s_reset9305_log[] = "RESET9305\r\n";     /* ROM 0x78b888 */
static const char s_appdb[] = "APPDB";                     /* ROM 0x78dffc */
static const char s_appdb_log[] = "PRINT ble database all records\r\n"; /* ROM 0x7582a4 */
static const char s_hostreset[] = "HOSTRESET";             /* ROM 0x78b894 */
static const char s_hostreset_log[] = "HOSTRESET\r\n";     /* ROM 0x78b8a0 */
static const char s_bles_bad[] =
    "AT^BLES [Bondable/Disbondable/DISCONN/RESET9305/HOSTRESET/APPDB]: The parameter is incorrect. "
    "Please enter the correct command %s %s\r\n"; /* ROM 0x6d50cc */
static const char s_scan[] = "Scan";                       /* ROM 0x78e004 */
static const char s_scan_log[] = "APP_MasterScanEvent true\r\n";     /* ROM 0x76fd14 */
static const char s_disscan[] = "DisScan";                 /* ROM 0x78e00c */
static const char s_disscan_log[] = "APP_MasterScanEvent false\r\n"; /* ROM 0x76fd30 */
static const char s_ringstate[] = "RINGSTATE";             /* ROM 0x78b8ac */
static const char s_connected[] = "connected";             /* ROM 0x78b8b8 */
static const char s_not_connected[] = "not connected";     /* ROM 0x788120 */
static const char s_ringstate_log[] = "RINGSTATE %s\r\n";  /* ROM 0x788110 */
static const char s_blem_bad[] =
    "AT^BLEM [Scan/DisScan/RINGSTATE]: The parameter is incorrect. Please enter the correct command "
    "%s %s\r\n"; /* ROM 0x6d969c */
static const char s_param1[] = "pcParameter1 = %s \r\n";   /* ROM 0x77a90c */
static const char s_param2[] = "pcParameter2 = %s \r\n";   /* ROM 0x77a924 */
static const char s_conn[] = "Conn";                       /* ROM 0x78e014 */
static const char s_conn_log[] = "APP_MasterConnectEvent true\r\n";  /* ROM 0x763b50 */
static const char s_conn_addr[] = "connect Addr %s\r\n";   /* ROM 0x78268c */
static const char s_hex_byte[] = "%02X ";                  /* ROM 0x78e01c */
static const char s_newline[] = "\n";                      /* ROM 0x581640 */
static const char s_addr_error[] = "addr error\n";         /* ROM 0x78b8c4 */
static const char s_disc[] = "Disc";                       /* ROM 0x78e024 */
static const char s_disc_log[] = "APP_MasterConnectEvent false\r\n"; /* ROM 0x763b70 */
static const char s_blemc_bad[] =
    "AT^BLEMC [Conn/Disc] [addr[5]:addr[4]:addr[3]:addr[2]:addr[1]:addr[0]]: The parameter is "
    "incorrect.  %s %s\r\n"; /* ROM 0x6d74a0 */
static const char s_start[] = "START";                     /* ROM 0x78e02c */
static const char s_start_log[] = "START\r\n";             /* ROM 0x78e034 */
static const char s_stop[] = "STOP";                       /* ROM 0x78e03c */
static const char s_stop_log[] = "STOP\r\n";               /* ROM 0x78e044 */
static const char s_state[] = "STATE";                     /* ROM 0x78e04c */
static const char s_adv_idle[] = "ADV state IDLE\r\n";     /* ROM 0x7826b4 */
static const char s_adv_advertising[] = "ADV state ADVERTISING\r\n"; /* ROM 0x77a954 */
static const char s_adv_stopping[] = "ADV state STOPPING\r\n"; /* ROM 0x77a96c */
static const char s_adv_starting[] = "ADV state STARTING\r\n"; /* ROM 0x77a984 */
static const char s_bleadv_bad[] =
    "AT^BLEADV [START/STOP/STATE]: The parameter is incorrect. Please enter the correct command "
    "%s %s\r\n"; /* ROM 0x6db5b0 */
static const char s_keep_connect[] = "_BleDoNotDisconnectBySelf %s\r\n"; /* ROM 0x763b90 */

int32_t cli_cmd_ble_get_mac_581150(char *write_buffer, size_t write_buffer_len,
                                   const char *command_string);
int32_t cli_cmd_ble_clean_bond_581180(char *write_buffer, size_t write_buffer_len,
                                      const char *command_string);
int32_t cli_cmd_ble_slave_58118a(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_ble_master_58125e(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_is_mac_string_5812ea(const char *text);
int32_t cli_parse_mac_581332(const char *text, uint8_t *out);
int32_t cli_cmd_ble_master_conn_58136c(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string);
int32_t cli_cmd_ble_adv_581564(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_ble_keep_connect_581628(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string);

/* "AT^BleGetMac": name and address, most significant byte first. */
int32_t cli_cmd_ble_get_mac_581150(char *write_buffer, size_t write_buffer_len,
                                   const char *command_string)
{
    const uint8_t *addr;
    const char *name;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    addr = APP_BleAddressGet();
    name = APP_BleNameGet();
    audio_ble_hci_boot_log_4733ee(s_get_mac, name, addr[5], addr[4], addr[3], addr[2], addr[1],
                                  addr[0]);
    return 0;
}

int32_t cli_cmd_ble_clean_bond_581180(char *write_buffer, size_t write_buffer_len,
                                      const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    app_clear_all_bonding_info_4b46ce();
    return 0;
}

/* "AT^BLES <op>": slave-side (phone link) controls. */
int32_t cli_cmd_ble_slave_58118a(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *op;

    (void)write_buffer;
    (void)write_buffer_len;
    op = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (string_compare_46cacc(op, s_bondable) == 0) {
        audio_ble_hci_boot_log_4733ee(s_bondable_log);
        audio_ble_app_adv_set_state(1u);
        AppAdvStart(1u);
    } else if (string_compare_46cacc(op, s_disbondable) == 0) {
        audio_ble_hci_boot_log_4733ee(s_disbondable_log);
        audio_ble_app_adv_set_state(0u);
    } else if (string_compare_46cacc(op, s_disconn) == 0) {
        audio_ble_hci_boot_log_4733ee(s_disconn_log);
        APP_BleSlaveDisconnect();
    } else if (string_compare_46cacc(op, s_reset9305) == 0) {
        audio_ble_hci_boot_log_4733ee(s_reset9305_log);
        ble_hci_radio_reset_4b4dc4();
    } else if (string_compare_46cacc(op, s_appdb) == 0) {
        audio_ble_hci_boot_log_4733ee(s_appdb_log);
        ble_appdb_print_all_47ca9c();
    } else if (string_compare_46cacc(op, s_hostreset) == 0) {
        audio_ble_hci_boot_log_4733ee(s_hostreset_log);
        app_ble_hw_error_reset_4b8224();
    } else {
        audio_ble_hci_boot_log_4733ee(s_bles_bad); /* stock passes no arguments for the %s */
    }
    return 0;
}

/* "AT^BLEM <op>": master-side (ring link) scan controls. */
int32_t cli_cmd_ble_master_58125e(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *op;

    (void)write_buffer;
    (void)write_buffer_len;
    op = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (string_compare_46cacc(op, s_scan) == 0) {
        audio_ble_hci_boot_log_4733ee(s_scan_log);
        APP_MasterScanEvent(BLE_SCAN_START);
    } else if (string_compare_46cacc(op, s_disscan) == 0) {
        audio_ble_hci_boot_log_4733ee(s_disscan_log);
        APP_MasterScanEvent(BLE_SCAN_STOP);
    } else if (string_compare_46cacc(op, s_ringstate) == 0) {
        audio_ble_hci_boot_log_4733ee(s_ringstate_log,
                                      audio_ble_master_is_connected_4a22c6() != 0u ? s_connected
                                                                                  : s_not_connected);
    } else {
        audio_ble_hci_boot_log_4733ee(s_blem_bad, command_string, op);
    }
    return 0;
}

/* 1 for "XX:XX:XX:XX:XX:XX" (17 chars, ':' at every third position). */
int32_t cli_is_mac_string_5812ea(const char *text)
{
    int32_t length = (int32_t)g2_log_module_length(text);
    int32_t i;

    if (length != (int32_t)BLE_MAC_TEXT_LENGTH)
        return 0;
    for (i = 0; i < length; i++) {
        if (i % 3 == 2) {
            if (text[i] != ':')
                return 0;
        } else if (iar_isxdigit_595984((uint8_t)text[i]) == 0) {
            return 0;
        }
    }
    return 1;
}

/* Text order is addr[5]..addr[0]; always returns 0. */
int32_t cli_parse_mac_581332(const char *text, uint8_t *out)
{
    char pair[3];
    int32_t index = (int32_t)BLE_MAC_BYTES - 1;
    int32_t i;

    (void)aeabi_memset_43c0e4(pair, sizeof(pair), 0);
    for (i = 0; i < (int32_t)BLE_MAC_TEXT_LENGTH; i += 3) {
        out[index] = (uint8_t)iar_strtol_595a2e(
            (const char *)audio_settings_copy_text(pair, text + i, 2u), NULL, 16);
        index--;
    }
    return 0;
}

/* "AT^BLEMC Conn <mac>" / "AT^BLEMC Disc". */
int32_t cli_cmd_ble_master_conn_58136c(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string)
{
    int32_t length = 0;
    uint8_t addr[BLE_MAC_BYTES];
    const char *op;
    const char *mac;
    uint32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    op = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    mac = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    audio_ble_hci_boot_log_4733ee(s_param1, op);
    audio_ble_hci_boot_log_4733ee(s_param2, mac);
    if (audio_ble_hci_vendor_compare_44b610(op, s_conn, 4u) == 0) {
        audio_ble_hci_boot_log_4733ee(s_conn_log);
        if (cli_is_mac_string_5812ea(mac) == 0)
            return 0;
        audio_ble_hci_boot_log_4733ee(s_conn_addr, mac);
        if (cli_parse_mac_581332(mac, addr) != 0) {
            audio_ble_hci_boot_log_4733ee(s_addr_error);
            return 0;
        }
        for (i = 0u; i < BLE_MAC_BYTES; i++)
            audio_ble_hci_boot_log_4733ee(s_hex_byte, addr[i]);
        audio_ble_hci_boot_log_4733ee(s_newline);
        APP_MasterSetTargetAddrName(addr, NULL, 0u);
        APP_MasterConnectEvent(BLE_MASTER_CONNECT);
    } else if (audio_ble_hci_vendor_compare_44b610(op, s_disc, 4u) == 0) {
        audio_ble_hci_boot_log_4733ee(s_disc_log);
        APP_MasterConnectEvent(BLE_MASTER_DISCONNECT);
    } else {
        audio_ble_hci_boot_log_4733ee(s_blemc_bad, command_string, op);
    }
    return 0;
}

/* "AT^BLEADV START|STOP|STATE": phone advertising via the event loop. */
int32_t cli_cmd_ble_adv_581564(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *op;
    uint8_t state;

    (void)write_buffer;
    (void)write_buffer_len;
    op = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (string_compare_46cacc(op, s_start) == 0) {
        audio_ble_hci_boot_log_4733ee(s_start_log);
        (void)fw_event_loop_remove_delayed(audio_ble_phone_advertising_restart);
        fw_event_loop_push_delayed(audio_ble_phone_advertising_restart, 0u, 0u);
    } else if (string_compare_46cacc(op, s_stop) == 0) {
        audio_ble_hci_boot_log_4733ee(s_stop_log);
        (void)fw_event_loop_remove_delayed(APP_BleSlaveAdvStopEvent);
        fw_event_loop_push_delayed(APP_BleSlaveAdvStopEvent, 0u, 0u);
    } else if (string_compare_46cacc(op, s_state) == 0) {
        (void)audio_ble_app_adv_state();
        state = audio_ble_dm_adv_state(0u);
        if (state == BLE_ADV_IDLE)
            audio_ble_hci_boot_log_4733ee(s_adv_idle);
        else if (state == BLE_ADV_ADVERTISING)
            audio_ble_hci_boot_log_4733ee(s_adv_advertising);
        else if (state == BLE_ADV_STOPPING)
            audio_ble_hci_boot_log_4733ee(s_adv_stopping);
        else if (state == BLE_ADV_STARTING)
            audio_ble_hci_boot_log_4733ee(s_adv_starting);
    } else {
        audio_ble_hci_boot_log_4733ee(s_bleadv_bad, command_string, op);
    }
    return 0;
}

/* "AT^BLE_KEEPCONNECT": stop the glasses dropping the phone link themselves. */
int32_t cli_cmd_ble_keep_connect_581628(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    slave_adv_stop_flag_or_0046f2dc(BLE_KEEP_CONNECT_FLAG);
    audio_ble_hci_boot_log_4733ee(s_keep_connect, command_string);
    return 0;
}
