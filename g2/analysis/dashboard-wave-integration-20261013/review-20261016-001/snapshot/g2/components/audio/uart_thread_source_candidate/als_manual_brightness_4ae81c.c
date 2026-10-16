/* Stock Apollo Main DRV_ALSManualSetBrightness, 0x4ae81c..0x4ae8d2. */
#include <stdint.h>

/* Bounded stock RAM cells; final address placement is a linker gate. */
uint32_t audio_als_manual_ready;      /* 0x200741c0 */
uint32_t audio_als_manual_level;      /* 0x200741f0 */
uint32_t audio_als_manual_level_copy; /* 0x200741f4 */
uint32_t audio_als_manual_pending;    /* 0x200741f8 */
extern uint32_t audio_als_active_previous;
extern uint32_t audio_als_default_previous;
extern uint32_t audio_als_scale_active;
extern uint32_t audio_als_curve_adjusted;
extern void audio_als_apply_previous(uint32_t);
extern void audio_als_manual_set_target_4ade36(uint32_t);
extern void audio_als_manual_recalculate_4adcd8(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "sensor_als";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\als\\als.c";
static const char function[] = "DRV_ALSManualSetBrightness";
static const char format[] = "manual brightness learn, brightness:%d, scale_q10:%d, target:%d";
static const char short_format[] = "[sensor_als]manual brightness learn, brightness:%d, scale_q10:%d, target:%d";

uint32_t audio_als_manual_set_brightness_4ae81c(uint32_t level)
{
    if (audio_als_manual_ready == 0u)
        return 1u;
    if (level > 100u)
        level = 100u;
    if (level < 2u)
        level = 2u;
    level &= ~1u;
    uint32_t previous = audio_als_active_previous;
    if (previous == 0u)
        previous = audio_als_default_previous;
    audio_als_apply_previous(previous);
    audio_als_manual_set_target_4ade36(level);
    audio_als_apply_previous(previous);
    audio_als_manual_recalculate_4adcd8();
    audio_als_manual_level = level;
    audio_als_manual_level_copy = level;
    audio_als_manual_pending = 1u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x295u, format,
                           level, audio_als_scale_active, audio_als_curve_adjusted);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u, short_format, short_format,
                                    level, audio_als_scale_active, audio_als_curve_adjusted);
    return 0u;
}
