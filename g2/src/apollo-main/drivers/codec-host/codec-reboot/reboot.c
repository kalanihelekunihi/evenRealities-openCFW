#include <stdint.h>

/* Complete local control flow of stock DRV_Gx8002_Reboot 0x57a816..0x57a86e.
 * Power off/on keep their distinct stock child contracts 0x57a5bc/0x57a508. */
extern void g2_codec_power_off(void);
extern void g2_codec_power_on(void);
extern void audio_delay(uint32_t ticks);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "drv.audio.codec";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\codec\\drv_gx8002b.c";
static const char function[] = "DRV_Gx8002_Reboot";
static const char done[] = "codec reboot done";
static const char simple_done[] = "[drv.audio.codec]codec reboot done";

void audio_special_control(uint32_t reboot_mode) {
    g2_codec_power_off();
    audio_delay(100u);
    g2_codec_power_on();
    if ((uint8_t)reboot_mode == 0u)
        audio_delay(1500u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, file, function, 185u, done);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, simple_done, simple_done);
}
