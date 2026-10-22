/* Settings service gates and KV savers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\settings\service_settings.c.
 * Native 0x46b334..0x46b3e4, 0x46b452..0x46b458, 0x46bef8..0x46bf60 and
 * 0x46bf74..0x46bfe4; literal pools 0x46bb70.., 0x46be0c, 0x46c000, 0x46c0d8 and
 * 0x46c660..0x46c6c3.
 *
 * Live settings record RAM 0x20072da8: +0x15 silent mode, +0x18 CRC16 of the first
 * 24 bytes, +0x20 ALS scale block (12 bytes, scale_q10 at +0x24), +0x2c ALS-dirty flag,
 * +0x44 runtime block (left-side version string, 9 bytes). */
#include <stdint.h>

extern uint8_t audio_settings_config_live[];  /* RAM 0x20072da8 */
extern uint8_t *audio_settings_config_previous; /* RAM 0x20003700 (manager 0x200036fc +4), last saved copy */

extern uint32_t productModeGet(void);                       /* 0x4abe60, 1 = factory test */
extern uint32_t semantic_OtaTransferActive(void);           /* 0x4487ac */
extern uint8_t *settings_get_config(void);                  /* 0x46b44c */
extern int32_t SVC_KvdbWriteSetting(const void *setting);   /* 0x4aec04 */
extern int32_t SVC_KvdbWriteAlsScale(const void *als);      /* 0x4aed88 */
extern void SVC_Settings_DumpSettingConfig(void);           /* 0x46b458 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "service.settings"; /* ROM 0x7835b4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c"; /* ROM 0x6e9ee0 */
static const char launch_fn[] = "SVC_Settings_AppLaunchCheck"; /* ROM 0x7715cc */
static const char launch_ota_msg[] = "OTA is going, app launch not allowed"; /* ROM 0x74e254 */
static const char launch_ota_short[] = "[service.settings]OTA is going, app launch not allowed"; /* ROM 0x722f58 */
static const char launch_silent_msg[] = "silent mode, app launch not allowed"; /* ROM 0x759d80 */
static const char launch_silent_short[] = "[service.settings]silent mode, app launch not allowed"; /* ROM 0x722f90 */
static const char save_fn[] = "SVC_Settings_SaveSettingConfigToKV"; /* ROM 0x759e34 */
static const char save_msg[] = "save setting config to kv"; /* ROM 0x7716c8 */
static const char save_short[] = "[service.settings]save setting config to kv"; /* ROM 0x7436fc */
static const char als_fn[] = "SVC_Settings_SaveAlsScaleToKV"; /* ROM 0x7652f0 */
static const char als_msg[] = "save als scale to kv, scale_q10:%d"; /* ROM 0x759e58 */
static const char als_short[] = "[service.settings]save als scale to kv, scale_q10:%d"; /* ROM 0x723000 */

static uint16_t load_u16(const uint8_t *p)
{
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}

/* 1 when an application may be launched: always in factory mode, never during OTA
 * or while silent mode is on. */
uint32_t SVC_Settings_AppLaunchCheck(void)
{
    if (productModeGet() == 1u)
        return 1u;
    if (semantic_OtaTransferActive() != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, launch_fn, 0x60u, launch_ota_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08000000u, launch_ota_short, launch_ota_short);
        return 0u;
    }
    if (settings_get_config()[0x15] == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, launch_fn, 0x66u, launch_silent_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08000000u, launch_silent_short, launch_silent_short);
        return 0u;
    }
    return 1u;
}

uint8_t *settings_get_runtime(void)
{
    return audio_settings_config_live + 0x44; /* RAM 0x20072dec */
}

/* Write the live record to KV when its CRC differs from the saved copy. */
uint32_t SVC_Settings_SaveSettingConfigToKV(void)
{
    if (load_u16(audio_settings_config_previous + 0x18) == load_u16(audio_settings_config_live + 0x18))
        return 0u;
    (void)SVC_KvdbWriteSetting(audio_settings_config_live);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, save_fn, 0x163u, save_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, save_short, save_short);
    SVC_Settings_DumpSettingConfig();
    return 0u;
}

uint32_t SVC_Settings_SaveAlsScaleToKV(void)
{
    uint8_t *live = audio_settings_config_live;
    if (live[0x2c] == 0u)
        return 0u;
    (void)SVC_KvdbWriteAlsScale(live + 0x20);
    live[0x2c] = 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, als_fn, 0x170u, als_msg,
                           *(const int32_t *)(const void *)(live + 0x24));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, als_short, als_short,
                                  *(const int32_t *)(const void *)(live + 0x24));
    return 0u;
}
