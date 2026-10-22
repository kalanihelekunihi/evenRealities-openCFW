/* Product FreeRTOS-Plus-CLI system and info command handlers, stock
 * directory D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 * prvCommand\ (file names not retained). Native: system handlers
 * 0x57e3e6..0x57e625 (inline "on"/"off" 0x57e668..0x57e66f, pool
 * 0x57e670..0x57e6a3), info helpers and handlers 0x57e6cc..0x57e80f (pool
 * 0x57e828..0x57e88b). "reset" 0x57e3d8 and both registrars are in
 * a-59-cli-commands/prvCommand_system.c.
 *
 * Handlers that answer through write_buffer use strncpy/snprintf with the
 * caller's buffer length; the rest print on the console. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define GPIO_WTSA_BASE 0x4001043cu /* GPIO WTSA0..: write-1-to-set output */
#define GPIO_WTCA_BASE 0x40010458u /* GPIO WTCA0..: write-1-to-clear output */
#define PRODUCT_MODE_RESET_DELAY_MS 100u
#define DIE_ID_BYTES 12u
#define CODEC_VERSION_BYTES 20u
#define CODEC_VERSION_TIMEOUT_MS 1000u
#define DEVICE_ROLE_CODEC 2u /* the arm that carries the GX8002 */

extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void productModeUpdate(uint8_t mode);         /* 0x4abe66 */
extern int32_t osDelay(uint32_t ticks);              /* 0x449376 */
extern void audio_ble_radio_ready_44b0ae(void);      /* system reset via 0x44ab24 */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern const uint32_t g2_sensor_rail_pin_config;     /* ROM 0x78ee40, value 0x183 (push-pull output) */
extern int32_t production_codec_mic_func_init(uint8_t channels); /* 0x58f69a */
extern int32_t production_codec_mic_func_deinit(void);           /* 0x58f74a */
extern void npmx_charger_enable_51299c(void);
extern void npmx_charger_disable_5128f8(void);
extern uint32_t am_devices_mspi_jbd4010_read_dieId(uint8_t *out);  /* 0x59308c */
extern uint32_t display_driver_uled_type0_get_592f9a(uint16_t *value); /* read_chipId */
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index);
extern uint8_t audio_uart_device_role_get(void);     /* 0x45a568 */
extern int32_t GX8002_ReadVersion(uint8_t version[4], uint32_t timeout); /* 0x57c664 */
extern const uint8_t *APP_BleAddressGet(void);       /* 0x4b80ea */
extern const char *APP_BleNameGet(void);             /* 0x46ed08 */
extern const char *semantic_TouchLogCurrentVersion(void); /* 0x561036 */
extern const char *SVC_NvdbReadSysData(uint32_t item);    /* 0x4af7b8 */
extern uint8_t *font_manager_xip_font_name_46d584(void);
extern void cmb_dump_thread_table_594334(void);
extern uint32_t ulSetInterruptMask(void);            /* 0x5fa0a4 */
extern char g2_codec_version_text_20073ce8[CODEC_VERSION_BYTES]; /* RAM 0x20073ce8 */

static const char s_clear_screen[] = "\x1b[2J\x1b[H\r\n#";          /* ROM 0x78b954 */
static const char s_missing_pin[] = "Error: Missing GPIO pin number\r\n"; /* ROM 0x758550 */
static const char s_gpio_high[] = "GPIO %lu set to HIGH\r\n";        /* ROM 0x77aaa4 */
static const char s_gpio_low[] = "GPIO %lu set to LOW\r\n";          /* ROM 0x77aabc */
static const char s_missing_param[] = "Error: Missing parameter\r\n"; /* ROM 0x76ffec */
static const char s_invalid_param[] = "Error: Invalid parameter\r\n"; /* ROM 0x770008 */
static const char s_on[] = "on";             /* ROM 0x57e668 */
static const char s_off[] = "off";           /* ROM 0x57e66c */
static const char s_enable[] = "enable";     /* ROM 0x78e184 */
static const char s_disable[] = "disable";   /* ROM 0x78e18c */
static const char s_die_id[] = "Die id:  %04x %04x %04x %04x %04x %04x\r\n"; /* ROM 0x741d34 */
static const char s_chip_id[] = "Chip id:  %04x\r\n";                        /* ROM 0x7827e0 */
static const char s_evt1[] = "EVT1";         /* ROM 0x78e1a4 */
static const char s_evt2[] = "EVT2";         /* ROM 0x78e1ac */
static const char s_evt3[] = "EVT3";         /* ROM 0x78e1b4 */
static const char s_dvt1[] = "DVT1";         /* ROM 0x78e1bc */
static const char s_dvt2[] = "DVT2";         /* ROM 0x78e1c4 */
static const char s_unknown[] = "Unknown";   /* ROM 0x78e1cc */
static const char s_version_fmt[] = "%d.%d.%d.%d"; /* ROM 0x78b96c */
static const char s_version_none[] = "0.0.0.0";    /* ROM 0x78e1d4 */
static const char s_product[] = "S200";            /* ROM 0x78e1dc */
static const char s_info_product[] = "Product name:       [%s]\r\n";  /* ROM 0x770024 */
static const char s_info_hw[] = "#Hardware version:  [%s]\r\n";       /* ROM 0x770040 */
static const char s_sw_version[] = "2.2.6.10";                         /* ROM 0x78b978 */
static const char s_info_sw[] = "#Software version:  [%s]\r\n";       /* ROM 0x77005c */
static const char s_git[] = "master:v2.2.6.10-0-gb79923a139f5";       /* ROM 0x758598 */
static const char s_info_git[] = "#Git describe full: [%s]\r\n";      /* ROM 0x770078 */
static const char s_info_codec[] = "#Codec    version:  [%s]\r\n";    /* ROM 0x770094 */
static const char s_info_touch[] = "#Touch    version:  [%s]\r\n";    /* ROM 0x7700b0 */
static const char s_build_time[] = "21:37:30";                         /* ROM 0x78b990 (__TIME__) */
static const char s_build_date[] = "Jul  6 2026";                      /* ROM 0x78b984 (__DATE__) */
static const char s_info_build[] = "#Build time:        [%s %s]\r\n"; /* ROM 0x763e50 */
static const char s_info_sn[] = "#Product SN:        [%s]\r\n";       /* ROM 0x7700cc */
static const char s_info_name[] = "#BLE NAME:          [%s]\r\n";     /* ROM 0x7700e8 */
static const char s_info_addr[] =
    "#BLE addr:          [%02X:%02X:%02X:%02X:%02X:%02X]\r\n"; /* ROM 0x721a20 */
static const char s_info_font[] = "#Font version:      [%s]\r\n";     /* ROM 0x770104 */

int32_t cli_cmd_clear_57e3e6(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_enter_product_mode_57e3f4(char *write_buffer, size_t write_buffer_len,
                                          const char *command_string);
int32_t cli_cmd_exit_product_mode_57e40a(char *write_buffer, size_t write_buffer_len,
                                         const char *command_string);
int32_t cli_cmd_set_gpio_57e420(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_reset_gpio_57e48e(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_product_control_codec_57e4fc(char *write_buffer, size_t write_buffer_len,
                                             const char *command_string);
int32_t cli_cmd_charger_control_57e55a(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string);
int32_t cli_cmd_read_die_id_57e5b6(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_read_chip_id_57e602(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string);
const char *hardware_version_string_57e6cc(void);
const char *codec_version_string_57e702(void);
int32_t cli_cmd_info_57e764(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_at_thread_57e7f6(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_at_dump_57e800(char *write_buffer, size_t write_buffer_len, const char *command_string);

int32_t cli_cmd_clear_57e3e6(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    (void)command_string;
    (void)audio_settings_copy_text(write_buffer, s_clear_screen, (uint32_t)write_buffer_len);
    return 0;
}

/* Persist the product-mode flag, then reset into it. */
int32_t cli_cmd_enter_product_mode_57e3f4(char *write_buffer, size_t write_buffer_len,
                                          const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    productModeUpdate(1u);
    (void)osDelay(PRODUCT_MODE_RESET_DELAY_MS);
    audio_ble_radio_ready_44b0ae();
    return 0;
}

int32_t cli_cmd_exit_product_mode_57e40a(char *write_buffer, size_t write_buffer_len,
                                         const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    productModeUpdate(0u);
    (void)osDelay(PRODUCT_MODE_RESET_DELAY_MS);
    audio_ble_radio_ready_44b0ae();
    return 0;
}

/* Decimal pin number from the token; non-digit characters are skipped. */
static uint32_t gpio_parse_pin(const char *text, int32_t length)
{
    uint32_t pin = 0u;
    int32_t i;

    for (i = 0; i < length; i++) {
        if ((uint32_t)(uint8_t)(text[i] - '0') < 10u)
            pin = pin * 10u + (uint32_t)(text[i] - '0');
    }
    return pin;
}

/* Configure the pin as a push-pull output and drive it through the
 * write-1 set/clear register bank selected by pin / 32. */
static int32_t gpio_drive(char *write_buffer, size_t write_buffer_len, const char *command_string,
                          uintptr_t bank_base, const char *done_format)
{
    int32_t length;
    const char *text;
    uint32_t pin;

    text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (text == NULL) {
        (void)audio_settings_copy_text(write_buffer, s_missing_pin, (uint32_t)write_buffer_len);
        return 0;
    }
    pin = gpio_parse_pin(text, length);
    (void)am_hal_gpio_pinconfig_480f0c(pin, g2_sensor_rail_pin_config);
    ((volatile uint32_t *)bank_base)[(pin >> 5) & 7u] = 1u << (pin & 31u);
    (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, done_format, pin);
    return 0;
}

int32_t cli_cmd_set_gpio_57e420(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    return gpio_drive(write_buffer, write_buffer_len, command_string, GPIO_WTSA_BASE, s_gpio_high);
}

int32_t cli_cmd_reset_gpio_57e48e(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    return gpio_drive(write_buffer, write_buffer_len, command_string, GPIO_WTCA_BASE, s_gpio_low);
}

/* "ProductControlCodec on|off": production mic path through the codec. */
int32_t cli_cmd_product_control_codec_57e4fc(char *write_buffer, size_t write_buffer_len,
                                             const char *command_string)
{
    int32_t length;
    const char *arg;

    arg = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (arg == NULL) {
        (void)audio_settings_copy_text(write_buffer, s_missing_param, (uint32_t)write_buffer_len);
    } else if (audio_ble_hci_vendor_compare_44b610(arg, s_on, 2u) == 0) {
        (void)production_codec_mic_func_init(1u);
    } else if (audio_ble_hci_vendor_compare_44b610(arg, s_off, 3u) == 0) {
        (void)production_codec_mic_func_deinit();
    } else {
        (void)audio_settings_copy_text(write_buffer, s_invalid_param, (uint32_t)write_buffer_len);
    }
    return 0;
}

/* "ChargerControl enable|disable": nPM charger on/off. */
int32_t cli_cmd_charger_control_57e55a(char *write_buffer, size_t write_buffer_len,
                                       const char *command_string)
{
    int32_t length;
    const char *arg;

    arg = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (arg == NULL) {
        (void)audio_settings_copy_text(write_buffer, s_missing_param, (uint32_t)write_buffer_len);
    } else if (audio_ble_hci_vendor_compare_44b610(arg, s_enable, 6u) == 0) {
        npmx_charger_enable_51299c();
    } else if (audio_ble_hci_vendor_compare_44b610(arg, s_disable, 7u) == 0) {
        npmx_charger_disable_5128f8();
    } else {
        (void)audio_settings_copy_text(write_buffer, s_invalid_param, (uint32_t)write_buffer_len);
    }
    return 0;
}

/* JBD4010 micro-LED panel die id: first six of the 12 read bytes. */
int32_t cli_cmd_read_die_id_57e5b6(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    uint8_t die_id[DIE_ID_BYTES];

    (void)command_string;
    (void)aeabi_memset_43c0e4(die_id, sizeof(die_id), 0);
    (void)am_devices_mspi_jbd4010_read_dieId(die_id);
    (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_die_id, die_id[0],
                                 die_id[1], die_id[2], die_id[3], die_id[4], die_id[5]);
    return 0;
}

int32_t cli_cmd_read_chip_id_57e602(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string)
{
    uint16_t chip_id = 0u;

    (void)command_string;
    (void)display_driver_uled_type0_get_592f9a(&chip_id);
    (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_chip_id, chip_id);
    return 0;
}

/* Board revision from radio-mode state byte 1: 1 EVT1, 2 EVT2, 3 EVT3,
 * 4 DVT1, 5 DVT2. */
const char *hardware_version_string_57e6cc(void)
{
    switch (*audio_ble_hci_radio_mode_state_50938e(1u)) {
    case 1u: return s_evt1;
    case 2u: return s_evt2;
    case 3u: return s_evt3;
    case 4u: return s_dvt1;
    case 5u: return s_dvt2;
    default: return s_unknown;
    }
}

/* GX8002 firmware version text; "0.0.0.0" on the arm without the codec. */
const char *codec_version_string_57e702(void)
{
    uint8_t version[4];

    (void)aeabi_memset_43c0e4(g2_codec_version_text_20073ce8, CODEC_VERSION_BYTES, 0);
    if (audio_uart_device_role_get() == DEVICE_ROLE_CODEC) {
        (void)aeabi_memset_43c0e4(version, sizeof(version), 0);
        (void)GX8002_ReadVersion(version, CODEC_VERSION_TIMEOUT_MS);
        (void)g2_audio_dump_snprintf(g2_codec_version_text_20073ce8, CODEC_VERSION_BYTES, s_version_fmt,
                                     version[0], version[1], version[2], version[3]);
    } else {
        (void)g2_audio_dump_snprintf(g2_codec_version_text_20073ce8, CODEC_VERSION_BYTES,
                                     s_version_none);
    }
    return g2_codec_version_text_20073ce8;
}

int32_t cli_cmd_info_57e764(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    const uint8_t *addr;
    const char *codec;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    addr = APP_BleAddressGet();
    codec = codec_version_string_57e702();
    audio_ble_hci_boot_log_4733ee(s_info_product, s_product);
    audio_ble_hci_boot_log_4733ee(s_info_hw, hardware_version_string_57e6cc());
    audio_ble_hci_boot_log_4733ee(s_info_sw, s_sw_version);
    audio_ble_hci_boot_log_4733ee(s_info_git, s_git);
    audio_ble_hci_boot_log_4733ee(s_info_codec, codec);
    audio_ble_hci_boot_log_4733ee(s_info_touch, semantic_TouchLogCurrentVersion());
    audio_ble_hci_boot_log_4733ee(s_info_build, s_build_date, s_build_time);
    audio_ble_hci_boot_log_4733ee(s_info_sn, SVC_NvdbReadSysData(0u));
    audio_ble_hci_boot_log_4733ee(s_info_name, APP_BleNameGet());
    audio_ble_hci_boot_log_4733ee(s_info_addr, addr[5], addr[4], addr[3], addr[2], addr[1], addr[0]);
    audio_ble_hci_boot_log_4733ee(s_info_font, font_manager_xip_font_name_46d584());
    return 0;
}

int32_t cli_cmd_at_thread_57e7f6(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    cmb_dump_thread_table_594334();
    return 0;
}

/* "AT^dump": mask interrupts and fault on a store to 0xffffffff so the
 * crash handler records a dump; never returns. */
int32_t cli_cmd_at_dump_57e800(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    (void)ulSetInterruptMask();
    *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    for (;;) {
    }
}
