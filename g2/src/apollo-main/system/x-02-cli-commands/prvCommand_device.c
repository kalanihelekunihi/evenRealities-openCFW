/* Product FreeRTOS-Plus-CLI device commands "buzzer", "gpio",
 * "box_force_out", "SetLanguage" and "onboarding" (one stock module each),
 * stock directory D:\01_workspace\s200_ap510b_iar_git\kernel\
 * FreeRTOS-Plus-CLI\prvCommand\ (file names not retained). Native:
 *   buzzer         0x583df8..0x583f73 (pool 0x583f80..0x583fbb)
 *   gpio level     0x583fbc..0x584029, gpio 0x58402a..0x5840f3
 *                  (inline "0"/"1"/"low" 0x584100..0x58410b, pool ..0x584127)
 *   box_force_out  0x584128..0x5841ed (inline "set" 0x5841f8, pool ..0x58421b)
 *   SetLanguage    0x58421c..0x58431f (inline codes 0x58432c..0x58433f,
 *                  pool 0x584340..0x58435b)
 *   onboarding     0x58435c..0x58442f (pool 0x58443c..0x58446f)
 * The registrars between them are in a-60-cli-commands/cli_command_register.c. */
#include <stddef.h>
#include <stdint.h>
#include "g2_hal_gpio.h"
#include "../a-59-cli-commands/cli_commands.h"

#define BUZZER_NOTE_COUNT 8
#define BUZZER_TONE_COUNT 4
#define LANGUAGE_SYNC_APP 0x20u
#define LANGUAGE_PB_BYTES 0x80u
#define LANGUAGE_WHICH 3u
#define ONBOARDING_INDEX 0u

/* nanopb pb_ostream_t */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "pb_ostream_t");

/* Module-configure package carrying the UI language (RAM 0x2037ce3c). */
typedef struct {
    uint8_t cmd;        /* +0x0 0 */
    uint8_t magic;      /* +0x1 0 */
    uint16_t which;     /* +0x2 3 = language */
    uint32_t language;  /* +0x4 0 en-GB .. 7 zh-HK */
} g2_language_cli_pkg_t;
_Static_assert(sizeof(g2_language_cli_pkg_t) == 8u, "language package");

extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t string_compare_46cacc(const char *a, const char *b);                            /* strcmp */
extern int32_t strncasecmp_595f0c(const char *a, const char *b, uint32_t len);
extern int32_t atoi_48d868(const char *text);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern void DRV_BuzzerPlayNote(uint8_t note, uint8_t tone, uint8_t beat); /* 0x502bf8 */
extern void DRV_BuzzerPlay(uint8_t effect);                                /* 0x502bf0 */
extern void DRV_BuzzerStart(uint32_t frequency, uint8_t duty);             /* 0x502c88 */
extern void DRV_BuzzerStop(void);                                          /* 0x502d4c */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value);          /* 0x53a5be */
/* Defined as void in drivers/power/box-detect; stock tests r0 here as the
 * sync send status (non-zero = failed). */
extern int32_t BoxDetect_SyncForceOutBox_4ac672(uint8_t force_out);
extern uint8_t BoxDetect_GetForceOutBox_4ac66a(void);
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* 0x490c32 */
extern const uint8_t g2_module_configure_pb_fields[];                      /* ROM 0x77979c */
extern int32_t audio_uart_input_event_send_464d1c(uint16_t app, const void *data, uint32_t len,
                                                  uint32_t flags); /* SendDataToBoth */
extern volatile uint8_t *SVC_KvdbReadOnboardingConfig(uint8_t index);       /* 0x4a7846 */
/* Stock tests r0 (0 = persisted). */
extern int32_t kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value); /* 0x4a7820 */
extern g2_language_cli_pkg_t g2_language_cli_pkg_2037ce3c;                 /* RAM 0x2037ce3c */
extern uint8_t g2_language_cli_pb_buffer_2037cdac[LANGUAGE_PB_BYTES];       /* RAM 0x2037cdac */

static const char s_buzzer_missing[] = "buzzer: Missing subcommand. Use 'note' or 'play'\r\n"; /* ROM 0x72c09c */
static const char s_note[] = "note";   /* ROM 0x78e06c */
static const char s_note_missing[] =
    "buzzer note: Missing parameters. Usage: buzzer note <note> <tone> <beat>\r\n"; /* ROM 0x6f55c0 */
static const char s_note_log[] = "Buzzer note: %d, tone: %d, beat: %d\r\n"; /* ROM 0x74ca94 */
static const char s_note_bad[] = "buzzer note: Parameters incorrect.\r\n";  /* ROM 0x74cabc */
static const char s_note_range[] = "note: 0-7, tone: 0-3, beat: >0\r\n";     /* ROM 0x7582ec */
static const char s_play[] = "play";   /* ROM 0x78e074 */
static const char s_play_missing[] =
    "buzzer play: Missing parameter. Usage: buzzer play <type>\r\n";         /* ROM 0x717bcc */
static const char s_play_log[] = "Buzzer play type: %d\r\n";                 /* ROM 0x77a99c */
static const char s_start[] = "start"; /* ROM 0x78e07c */
static const char s_start_missing[] =
    "buzzer start: Missing parameter. Usage: buzzer start <freq> <duty>\r\n"; /* ROM 0x6fc0bc */
static const char s_start_log[] = "Buzzer start freq: %d, duty: %d\r\n";     /* ROM 0x758310 */
static const char s_stop[] = "stop";   /* ROM 0x78e084 */
static const char s_buzzer_unknown[] =
    "buzzer: Unknown subcommand '%s'. Use 'note' or 'play'\r\n";             /* ROM 0x721978 */
static const char s_zero[] = "0";      /* ROM 0x584100 */
static const char s_one[] = "1";       /* ROM 0x584104 */
static const char s_low[] = "low";     /* ROM 0x584108 */
static const char s_high[] = "high";   /* ROM 0x78e164 */
static const char s_gpio_usage[] = "gpio: usage: gpio [num] [0|1|low|high]\r\n"; /* ROM 0x741cb0 */
static const char s_gpio_bad_level[] = "gpio: invalid level. use 0|1|low|high\r\n"; /* ROM 0x74cddc */
static const char s_gpio_init_failed[] = "gpio: init pin %u failed\r\n";     /* ROM 0x76ffb4 */
static const char s_gpio_write_failed[] = "gpio: write pin %u failed\r\n";   /* ROM 0x76ffd0 */
static const char s_gpio_done[] = "gpio: pin %u set %s\r\n";                 /* ROM 0x77aa8c */
static const char s_box_usage[] = "usage: box_force_out <set|clear|status>\r\n"; /* ROM 0x741b24 */
static const char s_set[] = "set";     /* ROM 0x5841f8 */
static const char s_clear[] = "clear"; /* ROM 0x78e054 */
static const char s_status[] = "status"; /* ROM 0x78e05c */
static const char s_box_failed[] = "box force out sync failed\r\n";          /* ROM 0x76fd4c */
static const char s_box_set[] = "box force out sync sent: set\r\n";          /* ROM 0x763bb0 */
static const char s_box_clear[] = "box force out sync sent: clear\r\n";      /* ROM 0x7582c8 */
static const char s_box_status[] = "box force out: %s\r\n";                  /* ROM 0x7826c8 */
static const char *const s_languages[] = {
    "en-GB", /* ROM 0x78e21c */
    "de",    /* ROM 0x58432c */
    "fr",    /* ROM 0x584330 */
    "es",    /* ROM 0x584334 */
    "it",    /* ROM 0x584338 */
    "ja",    /* ROM 0x58433c */
    "zh-CN", /* ROM 0x78e224 */
    "zh-HK", /* ROM 0x78e22c */
};
static const char s_onb_missing[] = "onboarding: missing parameters\r\n";    /* ROM 0x758628 */
static const char s_onb_usage[] = "Usage: onboarding getFlag | onboarding setFlag <0|1>\r\n"; /* ROM 0x721a58 */
static const char s_get_flag[] = "getFlag"; /* ROM 0x78e23c */
static const char s_onb_flag[] = "onboarding flag: %d\r\n";                  /* ROM 0x77ab04 */
static const char s_onb_read_failed[] = "onboarding: failed to read flag\r\n"; /* ROM 0x75864c */
static const char s_set_flag[] = "setFlag"; /* ROM 0x78e244 */
static const char s_onb_value_missing[] = "onboarding setFlag: missing flag value\r\n"; /* ROM 0x741d8c */
static const char s_onb_set_usage[] = "Usage: onboarding setFlag <0|1>\r\n"; /* ROM 0x758670 */
static const char s_onb_value_range[] = "onboarding setFlag: value must be 0 or 1\r\n"; /* ROM 0x741db8 */
static const char s_onb_set[] = "onboarding flag set to %d\r\n";             /* ROM 0x770120 */
static const char s_onb_set_failed[] = "onboarding: failed to set flag\r\n"; /* ROM 0x758694 */
static const char s_onb_unknown[] = "onboarding: unknown command\r\n";       /* ROM 0x763ed0 */

int32_t cli_cmd_buzzer_583df8(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t gpio_parse_level_583fbc(const char *text, uint8_t *level);
int32_t cli_cmd_gpio_58402a(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_box_force_out_584128(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string);
int32_t cli_cmd_set_language_58421c(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string);
int32_t cli_cmd_onboarding_58435c(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string);

/* "buzzer note <0-7> <0-3> <beat>|play <type>|start <freq> <duty>|stop" */
int32_t cli_cmd_buzzer_583df8(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *sub;
    const char *a;
    const char *b;
    const char *c;
    int32_t note;
    int32_t tone;
    int32_t beat;
    int32_t value;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (sub == NULL) {
        audio_ble_hci_boot_log_4733ee(s_buzzer_missing);
        return 0;
    }
    if (audio_ble_hci_vendor_compare_44b610(sub, s_note, 4u) == 0) {
        a = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        b = freertos_cli_get_parameter_5848fc(command_string, 3u, &length);
        c = freertos_cli_get_parameter_5848fc(command_string, 4u, &length);
        if (a == NULL || b == NULL || c == NULL) {
            audio_ble_hci_boot_log_4733ee(s_note_missing);
            return 0;
        }
        note = atoi_48d868(a);
        tone = atoi_48d868(b);
        beat = atoi_48d868(c);
        if ((uint32_t)note < BUZZER_NOTE_COUNT && (uint32_t)tone < BUZZER_TONE_COUNT && beat >= 1) {
            audio_ble_hci_boot_log_4733ee(s_note_log, note, tone, beat);
            DRV_BuzzerPlayNote((uint8_t)note, (uint8_t)tone, (uint8_t)beat);
        } else {
            audio_ble_hci_boot_log_4733ee(s_note_bad);
            audio_ble_hci_boot_log_4733ee(s_note_range);
        }
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_play, 4u) == 0) {
        a = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        if (a == NULL) {
            audio_ble_hci_boot_log_4733ee(s_play_missing);
            return 0;
        }
        value = atoi_48d868(a);
        audio_ble_hci_boot_log_4733ee(s_play_log, value);
        DRV_BuzzerPlay((uint8_t)value);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_start, 5u) == 0) {
        a = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        b = freertos_cli_get_parameter_5848fc(command_string, 3u, &length);
        if (a == NULL || b == NULL) {
            audio_ble_hci_boot_log_4733ee(s_start_missing);
            return 0;
        }
        value = atoi_48d868(a);
        beat = atoi_48d868(b);
        audio_ble_hci_boot_log_4733ee(s_start_log, value, beat);
        DRV_BuzzerStart((uint32_t)value, (uint8_t)beat);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_stop, 4u) == 0) {
        DRV_BuzzerStop();
    } else {
        audio_ble_hci_boot_log_4733ee(s_buzzer_unknown, sub);
    }
    return 0;
}

/* "0"/"1" exactly, or "low"/"high" case-insensitively; -1 otherwise. */
int32_t gpio_parse_level_583fbc(const char *text, uint8_t *level)
{
    if (text == NULL || level == NULL)
        return -1;
    if (string_compare_46cacc(text, s_zero) == 0) {
        *level = 0u;
        return 0;
    }
    if (string_compare_46cacc(text, s_one) == 0) {
        *level = 1u;
        return 0;
    }
    if (strncasecmp_595f0c(text, s_low, 3u) == 0) {
        *level = 0u;
        return 0;
    }
    if (strncasecmp_595f0c(text, s_high, 4u) == 0) {
        *level = 1u;
        return 0;
    }
    return -1;
}

/* "gpio <pin> <level>": configure the pin as an output through the board
 * GPIO HAL, then drive it. */
int32_t cli_cmd_gpio_58402a(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    g2_gpio_row_t row;
    const char *pin_text;
    const char *level_text;
    uint32_t pin;
    uint8_t level;

    (void)write_buffer;
    (void)write_buffer_len;
    pin_text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    level_text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    if (pin_text == NULL || level_text == NULL) {
        audio_ble_hci_boot_log_4733ee(s_gpio_usage);
        return 0;
    }
    pin = (uint32_t)atoi_48d868(pin_text);
    if (gpio_parse_level_583fbc(level_text, &level) != 0) {
        audio_ble_hci_boot_log_4733ee(s_gpio_bad_level);
        return 0;
    }
    (void)aeabi_memset_43c0e4(&row, sizeof(row), 0);
    row.pin = pin;
    row.mode = G2_GPIO_MODE_OUTPUT;
    row.level = level;
    row.int_dir = 0u;
    row.handler = NULL;
    if (board_gpio_table_init_53a454(&row, 1u) != 0) {
        audio_ble_hci_boot_log_4733ee(s_gpio_init_failed, pin);
        return 0;
    }
    if (g2_codec_pin_write(pin, level) != 0u) {
        audio_ble_hci_boot_log_4733ee(s_gpio_write_failed, pin);
        return 0;
    }
    audio_ble_hci_boot_log_4733ee(s_gpio_done, pin, level == 1u ? s_high : s_low);
    return 0;
}

/* "box_force_out set|clear|status": answers in write_buffer. */
int32_t cli_cmd_box_force_out_584128(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string)
{
    int32_t length;
    const char *sub;

    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (sub == NULL) {
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_usage);
        return 0;
    }
    if (audio_ble_hci_vendor_compare_44b610(sub, s_set, 3u) == 0) {
        if (BoxDetect_SyncForceOutBox_4ac672(1u) != 0)
            (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_failed);
        else
            (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_set);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_clear, 5u) == 0) {
        if (BoxDetect_SyncForceOutBox_4ac672(0u) != 0)
            (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_failed);
        else
            (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_clear);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_status, 6u) == 0) {
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_status,
                                     BoxDetect_GetForceOutBox_4ac66a() != 0u ? s_set : s_clear);
    } else {
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_box_usage);
    }
    return 0;
}

/* "SetLanguage <code>": encode a module-configure package with the
 * language index and push it to both arms (sync app 0x20). Unknown codes
 * and encode failures are silent. */
int32_t cli_cmd_set_language_58421c(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string)
{
    int32_t length;
    g2_pb_ostream_t created;
    g2_pb_ostream_t stream;
    g2_language_cli_pkg_t *pkg = &g2_language_cli_pkg_2037ce3c;
    const char *code;
    uint32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    code = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (code == NULL)
        return 0;
    (void)aeabi_memset_43c0e4(pkg, sizeof(*pkg), 0);
    pkg->cmd = 0u;
    pkg->magic = 0u;
    pkg->which = LANGUAGE_WHICH;
    pkg->language = 0u;
    for (i = 0u; i < sizeof(s_languages) / sizeof(s_languages[0]); i++) {
        if (string_compare_46cacc(code, s_languages[i]) == 0)
            break;
    }
    if (i == sizeof(s_languages) / sizeof(s_languages[0]))
        return 0;
    pkg->language = i;
    audio_pb_ostream_from_buffer(&created, g2_language_cli_pb_buffer_2037cdac, LANGUAGE_PB_BYTES);
    (void)aeabi_memcpy4_439c04(&stream, &created, sizeof(stream));
    if (audio_pb_encode(&stream, g2_module_configure_pb_fields, pkg) == 0u)
        return 0;
    (void)audio_uart_input_event_send_464d1c(LANGUAGE_SYNC_APP, g2_language_cli_pb_buffer_2037cdac,
                                             (uint16_t)stream.bytes_written, 0u);
    return 0;
}

/* "onboarding getFlag | setFlag <0|1>": KVDB onboarding flag 0. */
int32_t cli_cmd_onboarding_58435c(char *write_buffer, size_t write_buffer_len,
                                  const char *command_string)
{
    int32_t length = 0;
    volatile uint8_t *flag;
    const char *sub;
    const char *value_text;
    int32_t value;
    uint8_t new_flag;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (sub == NULL) {
        audio_ble_hci_boot_log_4733ee(s_onb_missing);
        audio_ble_hci_boot_log_4733ee(s_onb_usage);
        return 0;
    }
    if (strncasecmp_595f0c(sub, s_get_flag, 7u) == 0) {
        flag = SVC_KvdbReadOnboardingConfig(ONBOARDING_INDEX);
        if (flag != NULL)
            audio_ble_hci_boot_log_4733ee(s_onb_flag, *flag);
        else
            audio_ble_hci_boot_log_4733ee(s_onb_read_failed);
    } else if (strncasecmp_595f0c(sub, s_set_flag, 7u) == 0) {
        value_text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        if (value_text == NULL) {
            audio_ble_hci_boot_log_4733ee(s_onb_value_missing);
            audio_ble_hci_boot_log_4733ee(s_onb_set_usage);
            return 0;
        }
        value = atoi_48d868(value_text);
        if (value != 0 && value != 1) {
            audio_ble_hci_boot_log_4733ee(s_onb_value_range);
            audio_ble_hci_boot_log_4733ee(s_onb_set_usage);
            return 0;
        }
        new_flag = (uint8_t)value;
        if (kvdbOnboardingConfigUpdateAndPersist(ONBOARDING_INDEX, &new_flag) == 0)
            audio_ble_hci_boot_log_4733ee(s_onb_set, new_flag);
        else
            audio_ble_hci_boot_log_4733ee(s_onb_set_failed);
    } else {
        audio_ble_hci_boot_log_4733ee(s_onb_unknown);
        audio_ble_hci_boot_log_4733ee(s_onb_usage);
    }
    return 0;
}
