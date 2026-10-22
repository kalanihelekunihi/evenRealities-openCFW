/* Product FreeRTOS-Plus-CLI touch commands "tp" and "weardetect", stock
 * directory D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 * prvCommand\ (file name not retained). Native: helpers
 * 0x58198c..0x581a3f, tp 0x581a40..0x581d01 (inline "dfu" 0x581d04),
 * weardetect 0x581d08..0x581d5b (inline "%s" 0x581d5c, "cfg" 0x581d70),
 * pool 0x581d74..0x581ddf. The registrar 0x581d60 is in
 * a-59-cli-commands/prvCommand_registrars.c.
 *
 * tp drives the CY8C4046FNI touch/proximity controller:
 *   tp version | dfu [force] | reset | assert | diff | diff_always
 *   tp bsln_read | bsln_set | cfg read | cfg write <long_press_ms>
 * Sub-commands are matched case-insensitively (strncasecmp). */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define TP_TOKEN_BYTES 16u
#define TP_DIFF_CHANNELS 5u
#define TP_DIFF_ALWAYS_PERIOD_MS 500u
#define TP_CFG_READBACK_DELAY_MS 100u
#define WEAR_SYNC_TYPE_STATE 2u
#define WEAR_STATE_OFF 1u
#define WEAR_STATE_ON 2u

extern int32_t strncasecmp_595f0c(const char *a, const char *b, uint32_t len);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t strtoul_48d874(const char *text, char **end, int32_t base);
extern int32_t atoi_48d868(const char *text);
extern int32_t osDelay(uint32_t ticks); /* 0x449376 */
extern void cy8c4046fni_reset_55b64a(void);
extern int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version);
extern int32_t DRV_TouchReadSensorDiff_55b6a8(void *out);
extern int32_t DRV_TouchSaveProximityBaseline_55b730(void);
extern uint16_t DRV_TouchReadProximityBaseline_55b78a(void);
extern int32_t DRV_TouchWriteGestureCfg_55b840(const uint16_t *threshold);
extern int32_t DRV_TouchReadGestureCfg_55b92a(uint16_t *threshold);
extern void TouchUpdateFirmwareCheck(uint8_t force); /* 0x56110c */
extern int32_t wear_detect_sync_send_49eae2(uint8_t type, uint32_t value);
extern g2_cli_command_t g2_cli_cmd_tp_20003634;         /* "tp", variable */

static const char s_gesture_cfg[] = "Gesture cfg: long_press_threshold_ms=%u\r\n"; /* ROM 0x741f18 */
static const char s_percent_s[] = "%s";            /* ROM 0x581d5c */
static const char s_version[] = "version";         /* ROM 0x78e394 */
static const char s_version_log[] = "tp version:%d.%d.%d.%d\r\n"; /* ROM 0x77036c */
static const char s_dfu[] = "dfu";                 /* ROM 0x581d04 */
static const char s_force[] = "force";             /* ROM 0x78e39c */
static const char s_reset[] = "reset";             /* ROM 0x78e3a4 */
static const char s_assert[] = "assert";           /* ROM 0x78e3ac */
static const char s_diff_always[] = "diff_always"; /* ROM 0x78bb88 */
static const char s_diff_log[] = "diff: %u, %u, %u, %u, %u\r\n"; /* ROM 0x770388 */
static const char s_diff[] = "diff";               /* ROM 0x78e3b4 */
static const char s_bsln_read[] = "bsln_read";     /* ROM 0x78bb94 */
static const char s_bsln_log[] = "Proximity baseline: %u\r\n"; /* ROM 0x7703a4 */
static const char s_bsln_set[] = "bsln_set";       /* ROM 0x78bba0 */
static const char s_bsln_saved[] =
    "Proximity baseline save command sent successfully.\r\n"; /* ROM 0x721b00 */
static const char s_cfg[] = "cfg";                 /* ROM 0x581d70 */
static const char s_cfg_usage[] = "Usage: tp cfg <read|write> [threshold_ms]\r\n"; /* ROM 0x741f44 */
static const char s_read[] = "read";               /* ROM 0x78e3bc */
static const char s_cfg_read_failed[] = "Gesture cfg read failed.\r\n"; /* ROM 0x7703c0 */
static const char s_write[] = "write";             /* ROM 0x78e3c4 */
static const char s_cfg_write_usage[] = "Usage: tp cfg write <threshold_ms>\r\n"; /* ROM 0x74d14c */
static const char s_cfg_bad_value[] =
    "Invalid long_press_threshold_ms. It must be an integer > 0.\r\n"; /* ROM 0x70e1a4 */
static const char s_cfg_write_failed[] = "Gesture cfg write failed.\r\n"; /* ROM 0x7703dc */
static const char s_cfg_readback_failed[] =
    "Gesture cfg write success, but readback failed.\r\n"; /* ROM 0x72c374 */
static const char s_cfg_mismatch[] =
    "Gesture cfg write mismatch: wrote threshold=%u, read back threshold=%u\r\n"; /* ROM 0x6f5820 */
static const char s_cfg_verified[] = "Gesture cfg updated and verified successfully.\r\n"; /* ROM 0x72c3a8 */
static const char s_tp_invalid[] = "tp: invalid parameter.\r\n%s"; /* ROM 0x7703f8 */
static const char s_state[] = "state";             /* ROM 0x78e3cc */

int32_t cli_copy_token_58198c(const char *text, uint32_t length, char *out, uint32_t capacity);
int32_t cli_parse_u16_5819c8(const char *text, uint32_t length, uint16_t *out);
void tp_print_gesture_cfg_581a2e(const uint16_t *threshold);
int32_t cli_cmd_tp_581a40(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_weardetect_581d08(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string);

/* Copy a CLI token (not NUL-terminated in the command line) into out. */
int32_t cli_copy_token_58198c(const char *text, uint32_t length, char *out, uint32_t capacity)
{
    if (text == NULL || out == NULL || capacity == 0u || (int32_t)length < 1)
        return -1;
    if (length >= capacity)
        return -1;
    (void)audio_queue_copy_bytes(out, text, length);
    out[length] = '\0';
    return 0;
}

/* Decimal token -> u16; -1 when empty, trailing garbage or > 0xffff. */
int32_t cli_parse_u16_5819c8(const char *text, uint32_t length, uint16_t *out)
{
    char token[TP_TOKEN_BYTES];
    char *end;
    uint32_t value;

    (void)aeabi_memset_43c0e4(token, sizeof(token), 0);
    end = NULL;
    if (out == NULL || cli_copy_token_58198c(text, length, token, sizeof(token)) != 0)
        return -1;
    value = strtoul_48d874(token, &end, 10);
    if (end == token || *end != '\0' || value >= 0x10000u)
        return -1;
    *out = (uint16_t)value;
    return 0;
}

void tp_print_gesture_cfg_581a2e(const uint16_t *threshold)
{
    if (threshold != NULL)
        audio_ble_hci_boot_log_4733ee(s_gesture_cfg, *threshold);
}

static void tp_print_diff(void)
{
    uint16_t diff[TP_DIFF_CHANNELS];

    (void)aeabi_memset_43c0e4(diff, sizeof(diff), 0);
    (void)DRV_TouchReadSensorDiff_55b6a8(diff);
    audio_ble_hci_boot_log_4733ee(s_diff_log, diff[0], diff[1], diff[2], diff[3], diff[4]);
}

static void tp_cfg_write(const char *value_text, int32_t value_length)
{
    uint16_t wanted;
    uint16_t readback;

    (void)aeabi_memset_43c0e4(&wanted, sizeof(wanted), 0);
    (void)aeabi_memset_43c0e4(&readback, sizeof(readback), 0);
    if (value_text == NULL) {
        audio_ble_hci_boot_log_4733ee(s_cfg_write_usage);
        return;
    }
    if (cli_parse_u16_5819c8(value_text, (uint32_t)value_length, &wanted) != 0 || wanted == 0u) {
        audio_ble_hci_boot_log_4733ee(s_cfg_bad_value);
        return;
    }
    if (DRV_TouchWriteGestureCfg_55b840(&wanted) != 0) {
        audio_ble_hci_boot_log_4733ee(s_cfg_write_failed);
        return;
    }
    (void)osDelay(TP_CFG_READBACK_DELAY_MS);
    if (DRV_TouchReadGestureCfg_55b92a(&readback) != 0) {
        audio_ble_hci_boot_log_4733ee(s_cfg_readback_failed);
        return;
    }
    if (readback != wanted) {
        audio_ble_hci_boot_log_4733ee(s_cfg_mismatch, wanted, readback);
        return;
    }
    audio_ble_hci_boot_log_4733ee(s_cfg_verified);
    tp_print_gesture_cfg_581a2e(&readback);
}

int32_t cli_cmd_tp_581a40(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length1 = 0;
    int32_t length2 = 0;
    int32_t length3 = 0;
    uint32_t version;
    uint16_t threshold;
    const char *sub;
    const char *arg;
    const char *value;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length1);
    arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length2);
    value = freertos_cli_get_parameter_5848fc(command_string, 3u, &length3);

    if (sub == NULL) {
        audio_ble_hci_boot_log_4733ee(s_percent_s, g2_cli_cmd_tp_20003634.help);
    } else if (strncasecmp_595f0c(sub, s_version, 7u) == 0) {
        version = 0u;
        (void)cy8c4046fni_read_version_55b6dc(&version);
        audio_ble_hci_boot_log_4733ee(s_version_log, version >> 24, (version >> 16) & 0xffu,
                                      (version >> 8) & 0xffu, version & 0xffu);
    } else if (strncasecmp_595f0c(sub, s_dfu, 3u) == 0) {
        if (arg != NULL && strncasecmp_595f0c(arg, s_force, 5u) == 0)
            TouchUpdateFirmwareCheck(1u);
        else
            TouchUpdateFirmwareCheck(0u);
    } else if (strncasecmp_595f0c(sub, s_reset, 5u) == 0) {
        cy8c4046fni_reset_55b64a();
    } else if (strncasecmp_595f0c(sub, s_assert, 6u) == 0) {
        /* Deliberate fault: store to 0xffffffff. */
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    } else if (strncasecmp_595f0c(sub, s_diff_always, 11u) == 0) {
        for (;;) {
            (void)osDelay(TP_DIFF_ALWAYS_PERIOD_MS);
            tp_print_diff();
        }
    } else if (strncasecmp_595f0c(sub, s_diff, 4u) == 0) {
        tp_print_diff();
    } else if (strncasecmp_595f0c(sub, s_bsln_read, 9u) == 0) {
        audio_ble_hci_boot_log_4733ee(s_bsln_log, DRV_TouchReadProximityBaseline_55b78a());
    } else if (strncasecmp_595f0c(sub, s_bsln_set, 8u) == 0) {
        cy8c4046fni_reset_55b64a();
        version = 0u;
        (void)cy8c4046fni_read_version_55b6dc(&version);
        (void)DRV_TouchSaveProximityBaseline_55b730();
        audio_ble_hci_boot_log_4733ee(s_bsln_saved);
    } else if (strncasecmp_595f0c(sub, s_cfg, 3u) == 0) {
        if (arg == NULL) {
            audio_ble_hci_boot_log_4733ee(s_cfg_usage);
        } else if (strncasecmp_595f0c(arg, s_read, 4u) == 0) {
            (void)aeabi_memset_43c0e4(&threshold, sizeof(threshold), 0);
            if (DRV_TouchReadGestureCfg_55b92a(&threshold) == 0)
                tp_print_gesture_cfg_581a2e(&threshold);
            else
                audio_ble_hci_boot_log_4733ee(s_cfg_read_failed);
        } else if (strncasecmp_595f0c(arg, s_write, 5u) == 0) {
            tp_cfg_write(value, length3);
        } else {
            audio_ble_hci_boot_log_4733ee(s_cfg_usage);
        }
    } else {
        audio_ble_hci_boot_log_4733ee(s_tp_invalid, g2_cli_cmd_tp_20003634.help);
    }
    return 0;
}

/* "weardetect state <0|1>": inject a wear state into the wear-detect sync. */
int32_t cli_cmd_weardetect_581d08(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string)
{
    int32_t length1 = 0;
    int32_t length2 = 0;
    const char *sub;
    const char *arg;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length1);
    arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length2);
    if (strncasecmp_595f0c(sub, s_state, 5u) == 0)
        (void)wear_detect_sync_send_49eae2(WEAR_SYNC_TYPE_STATE,
                                           atoi_48d868(arg) != 0 ? WEAR_STATE_ON : WEAR_STATE_OFF);
    return 0;
}
