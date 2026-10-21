/* Native HUB_ParameterConfig, 0x4a6e3c..0x4a6eca. */
#include <stdint.h>

extern volatile uint16_t audio_uart_hub_role_cell; /* stock RAM 0x20004526 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_hub_semantic_motion_threshold_4a4e8c(uint32_t);
extern uint32_t audio_hub_semantic_motion_period_4a4ec0(uint32_t, uint32_t);
extern uint32_t audio_hub_imu_accel_config_4a52a2(uint32_t);

static const char module[] = "sensor_hub";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c";
static const char function[] = "HUB_ParameterConfig";
static const char denied[] = "IMU open role type is left, cannot config";
static const char denied_short[] = "[sensor_hub]IMU open role type is left, cannot config";

uint32_t audio_hub_parameter_config_4a6e3c(uint32_t type,
                                             const int32_t *params)
{
    if (audio_uart_hub_role_cell == 2u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x1a1u, denied);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, denied_short,
                                        denied_short);
        return UINT32_MAX;
    }
    switch ((uint8_t)type) {
    case 1u:
        audio_hub_semantic_motion_threshold_4a4e8c((uint32_t)params[0]);
        break;
    case 2u:
        (void)audio_hub_semantic_motion_period_4a4ec0((uint32_t)params[0],
                                                       (uint32_t)params[1]);
        break;
    case 5u:
        (void)audio_hub_imu_accel_config_4a52a2((uint32_t)params[0]);
        break;
    default:
        break;
    }
    return 0u;
}
