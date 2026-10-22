/* Product FreeRTOS-Plus-CLI audio commands "audm" and "codec", stock
 * directory D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 * prvCommand\ (file name not retained). Native: audm 0x580c7c..0x580d17,
 * codec 0x580d18..0x580fe1, inline strings 0x580fe4..0x580feb and
 * 0x580ffc..0x58100f, pool 0x581010..0x58109b. The registrar 0x580fec is
 * in a-59-cli-commands/prvCommand_registrars.c.
 *
 *   audm acquire|release <app>, audm status   audio-manager app slots 1..7
 *   codec dfu force|check                      GX8002 firmware update
 *   codec open|close                           audio stream message
 *   codec mic state|on|off|gain <0-48>         GX8002 DMIC
 *   codec mode bf|wakeup, version, reset, powerdown, poweron
 *   codec i2s on|off, production on|off */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define AUDM_APP_SLOTS 8
#define CODEC_MIC_GAIN_MAX 48
#define CODEC_MIC_STATE_TIMEOUT_MS 200u
#define CODEC_VERSION_TIMEOUT_MS 1000u

extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t atoi_48d868(const char *text);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t AUDM_appAcquire(uint32_t user); /* 0x54f380 */
extern int32_t AUDM_appRelease(uint32_t user); /* 0x54f50e */
extern uint8_t g2_audio_app_acquired[8];       /* RAM 0x20074180 */
extern void aud_send_message_type0(uint32_t value); /* 0x53ca10 */
extern void aud_send_message_type4(uint8_t value);  /* 0x53ca54 */
extern int32_t GX8002_QueryMicState(uint16_t *state, uint32_t timeout); /* 0x57cb60 */
extern int32_t GX8002_ReadVersion(uint8_t version[4], uint32_t timeout); /* 0x57c664 */
extern int32_t audio_dsp_enable(void);       /* SVC_CodecDMICOpen 0x57d6b4 */
extern int32_t audio_dsp_disable(void);      /* SVC_CodecDMICClose 0x57d794 */
extern int32_t audio_dsp_gate(uint32_t on);  /* SVC_I2SOutputCtrl 0x57d93c */
extern int32_t SVC_SetMicGain(uint8_t gain); /* 0x57d5c0 */
extern int32_t SVC_SwitchBFMode(void);       /* 0x57d418 */
extern int32_t SVC_SwitchWakeupMode(void);   /* 0x57d4e4 */
extern void DRV_Gx8002_Reboot(uint8_t skip_boot_wait); /* 0x57a816 */
extern void DRV_Gx8002_PowerOn(void);        /* 0x57a508 */
extern void DRV_Gx8002_PowerOff(void);       /* 0x57a5bc */
extern int32_t production_codec_mic_func_init(uint8_t channels); /* 0x58f69a */
extern int32_t production_codec_mic_func_deinit(void);           /* 0x58f74a */

static const char s_acquire[] = "acquire";  /* ROM 0x78e09c */
static const char s_release[] = "release";  /* ROM 0x78e0a4 */
static const char s_status[] = "status";    /* ROM 0x78e0ac */
static const char s_audm_status[] = "[app:%d] status: %d\r\n"; /* ROM 0x77a9b4 */
static const char s_audm_bad[] =
    "audm: The parameter is incorrect. Please enter the correct command\r\n"; /* ROM 0x6fc104 */
static const char s_dfu[] = "dfu";          /* ROM 0x580fe4 */
static const char s_force[] = "force";      /* ROM 0x78e0b4 */
static const char s_check[] = "check";      /* ROM 0x78e0bc */
static const char s_open[] = "open";        /* ROM 0x78e0c4 */
static const char s_close[] = "close";      /* ROM 0x78e0cc */
static const char s_mic[] = "mic";          /* ROM 0x580fe8 */
static const char s_state[] = "state";      /* ROM 0x78e0d4 */
static const char s_on[] = "on";            /* ROM 0x580ffc */
static const char s_ok[] = "ok";            /* ROM 0x581000 */
static const char s_off[] = "off";          /* ROM 0x581004 */
static const char s_bf[] = "bf";            /* ROM 0x581008 */
static const char s_i2s[] = "i2s";          /* ROM 0x58100c */
static const char s_fail[] = "fail";        /* ROM 0x78e0dc */
static const char s_gain[] = "gain";        /* ROM 0x78e0e4 */
static const char s_mode[] = "mode";        /* ROM 0x78e0ec */
static const char s_wakeup[] = "wakeup";    /* ROM 0x78e0f4 */
static const char s_version[] = "version";  /* ROM 0x78e0fc */
static const char s_reset[] = "reset";      /* ROM 0x78e104 */
static const char s_powerdown[] = "powerdown"; /* ROM 0x78b8dc */
static const char s_poweron[] = "poweron";  /* ROM 0x78e10c */
static const char s_production[] = "production"; /* ROM 0x78b8e8 */
static const char s_mic_state[] = "codec: mic state: 0x%04X\r\n"; /* ROM 0x76fd68 */
static const char s_dmic_on[] = "codec: dmic on %s\r\n";          /* ROM 0x7826dc */
static const char s_dmic_off[] = "codec: dmic off %s\r\n";        /* ROM 0x77a9cc */
static const char s_gain_missing[] =
    "codec: mic gain missing value. usage: codec mic gain <0-48>\r\n"; /* ROM 0x70dee4 */
static const char s_gain_range[] = "codec: mic gain out of range (0-48)\r\n"; /* ROM 0x74cae4 */
static const char s_gain_set[] = "codec: set mic gain %d %s\r\n";              /* ROM 0x76fd84 */
static const char s_mic_bad[] =
    "codec: mic subcommand invalid. use: mic state | mic gain <0-48> | mic on|off\r\n"; /* ROM 0x6ef188 */
static const char s_version_log[] = "codec: version: %d.%d.%d.%d\r\n"; /* ROM 0x763bd0 */
static const char s_powerdown_ok[] = "codec: powerdown ok\r\n";        /* ROM 0x77a9e4 */
static const char s_poweron_ok[] = "codec: poweron ok\r\n";            /* ROM 0x7826f0 */
static const char s_i2s_on[] = "codec: i2s on %s\r\n";                 /* ROM 0x782704 */
static const char s_i2s_off[] = "codec: i2s off %s\r\n";               /* ROM 0x782718 */
static const char s_codec_bad[] =
    "codec: The parameter is incorrect. Please enter the correct command\r\n"; /* ROM 0x6fc14c */

int32_t cli_cmd_audm_580c7c(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_codec_580d18(char *write_buffer, size_t write_buffer_len, const char *command_string);

int32_t cli_cmd_audm_580c7c(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    int32_t length2 = 0;
    const char *sub;
    int32_t app;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (audio_ble_hci_vendor_compare_44b610(sub, s_acquire, 7u) == 0) {
        app = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length2));
        (void)AUDM_appAcquire((uint8_t)app);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_release, 7u) == 0) {
        app = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length2));
        (void)AUDM_appRelease((uint8_t)app);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_status, 6u) == 0) {
        for (app = 1; app < AUDM_APP_SLOTS; app++)
            audio_ble_hci_boot_log_4733ee(s_audm_status, app, g2_audio_app_acquired[app]);
    } else {
        audio_ble_hci_boot_log_4733ee(s_audm_bad);
    }
    return 0;
}

/* "ok" for a 0 status, "fail" otherwise. */
static const char *codec_result(int32_t status)
{
    return status == 0 ? s_ok : s_fail;
}

int32_t cli_cmd_codec_580d18(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    uint8_t version[4];
    uint16_t mic_state;
    const char *sub;
    const char *arg;
    const char *value_text;
    int32_t gain;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);

    if (audio_ble_hci_vendor_compare_44b610(sub, s_dfu, 3u) == 0) {
        if (audio_ble_hci_vendor_compare_44b610(arg, s_force, 5u) == 0)
            aud_send_message_type4(1u);
        else if (audio_ble_hci_vendor_compare_44b610(arg, s_check, 5u) == 0)
            aud_send_message_type4(0u);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_open, 4u) == 0) {
        aud_send_message_type0(1u);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_close, 5u) == 0) {
        aud_send_message_type0(0u);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_mic, 3u) == 0) {
        if (audio_ble_hci_vendor_compare_44b610(arg, s_state, 5u) == 0) {
            (void)aeabi_memset_43c0e4(&mic_state, sizeof(mic_state), 0);
            (void)GX8002_QueryMicState(&mic_state, CODEC_MIC_STATE_TIMEOUT_MS);
            audio_ble_hci_boot_log_4733ee(s_mic_state, mic_state);
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_on, 2u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_dmic_on, codec_result(audio_dsp_enable()));
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_off, 3u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_dmic_off, codec_result(audio_dsp_disable()));
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_gain, 4u) == 0) {
            value_text = freertos_cli_get_parameter_5848fc(command_string, 3u, &length);
            if (value_text == NULL) {
                audio_ble_hci_boot_log_4733ee(s_gain_missing);
            } else {
                gain = atoi_48d868(value_text);
                if ((uint32_t)gain > (uint32_t)CODEC_MIC_GAIN_MAX)
                    audio_ble_hci_boot_log_4733ee(s_gain_range);
                else
                    audio_ble_hci_boot_log_4733ee(s_gain_set, gain,
                                                  codec_result(SVC_SetMicGain((uint8_t)gain)));
            }
        } else {
            audio_ble_hci_boot_log_4733ee(s_mic_bad);
        }
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_mode, 4u) == 0) {
        if (audio_ble_hci_vendor_compare_44b610(arg, s_bf, 2u) == 0)
            (void)SVC_SwitchBFMode();
        else if (audio_ble_hci_vendor_compare_44b610(arg, s_wakeup, 6u) == 0)
            (void)SVC_SwitchWakeupMode();
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_version, 7u) == 0) {
        (void)aeabi_memset_43c0e4(version, sizeof(version), 0);
        (void)GX8002_ReadVersion(version, CODEC_VERSION_TIMEOUT_MS);
        audio_ble_hci_boot_log_4733ee(s_version_log, version[0], version[1], version[2], version[3]);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_reset, 5u) == 0) {
        DRV_Gx8002_Reboot(0u);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_powerdown, 9u) == 0) {
        DRV_Gx8002_PowerOff();
        audio_ble_hci_boot_log_4733ee(s_powerdown_ok);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_poweron, 7u) == 0) {
        DRV_Gx8002_PowerOn();
        audio_ble_hci_boot_log_4733ee(s_poweron_ok);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_i2s, 3u) == 0) {
        if (audio_ble_hci_vendor_compare_44b610(arg, s_on, 2u) == 0)
            audio_ble_hci_boot_log_4733ee(s_i2s_on, codec_result(audio_dsp_gate(1u)));
        else if (audio_ble_hci_vendor_compare_44b610(arg, s_off, 3u) == 0)
            audio_ble_hci_boot_log_4733ee(s_i2s_off, codec_result(audio_dsp_gate(0u)));
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_production, 10u) == 0) {
        if (audio_ble_hci_vendor_compare_44b610(arg, s_on, 2u) == 0)
            (void)production_codec_mic_func_init(1u);
        else if (audio_ble_hci_vendor_compare_44b610(arg, s_off, 3u) == 0)
            (void)production_codec_mic_func_deinit();
    } else {
        audio_ble_hci_boot_log_4733ee(s_codec_bad);
    }
    return 0;
}
