/* Native DRV_IMUAccelConfig, 0x4a52a2..0x4a5308. */
#include <stdint.h>

uint32_t audio_hub_imu_report_interval_cell; /* stock RAM 0x20000e60 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "sensor_imu";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\imu\\imu_icm45608.c";
static const char function[] = "DRV_IMUAccelConfig";
static const char format[] = "DRV_IMUAccelConfig report_interval = %d";
static const char short_format[] = "[sensor_imu]DRV_IMUAccelConfig report_interval = %d";

uint32_t audio_hub_imu_accel_config_4a52a2(uint32_t interval)
{
    if (interval - 100u >= 0x1325u)
        return UINT32_MAX;
    audio_hub_imu_report_interval_cell = interval;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, 0x489u,
                           format, interval);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x08400000u, short_format,
                                    short_format, interval);
    return 0u;
}
