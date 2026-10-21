#include <stdint.h>

/* Stock 0x57a508 and 0x57a5bc. The source-owned product state byte
 * must be placed at stock 0x20074fb6 for a stock-compatible image. */
extern uint8_t g2_codec_power_state;
extern uint32_t g2_codec_gpio_write(uint32_t line, uint32_t value,
                                     uint32_t unused_r2, uint32_t passthrough_r3);
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
static const char on_function[] = "DRV_Gx8002_PowerOn";
static const char off_function[] = "DRV_Gx8002_PowerOff";
static const char already_on[] = "gx8002 already power on.";
static const char powered_on[] = "gx8002 power on.";
static const char already_off[] = "gx8002 already power off.";
static const char powered_off[] = "gx8002 power off.";
static const char simple_already_on[] = "[drv.audio.codec]gx8002 already power on.";
static const char simple_powered_on[] = "[drv.audio.codec]gx8002 power on.";
static const char simple_already_off[] = "[drv.audio.codec]gx8002 already power off.";
static const char simple_powered_off[] = "[drv.audio.codec]gx8002 power off.";

static void log_state(uint32_t line, const char *function,
                      const char *message, const char *simple) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, simple, simple);
}

void g2_codec_power_on(void) {
    if (g2_codec_power_state != 0u) {
        log_state(87u, on_function, already_on, simple_already_on);
        return;
    }
    g2_codec_power_state = 1u;
    (void)g2_codec_gpio_write(6u, 1u, 0u, 0u);
    audio_delay(5u);
    (void)g2_codec_gpio_write(7u, 1u, 0u, 0u);
    audio_delay(20u);
    (void)g2_codec_gpio_write(8u, 1u, 0u, 0u);
    log_state(97u, on_function, powered_on, simple_powered_on);
}

void g2_codec_power_off(void) {
    if (g2_codec_power_state == 0u) {
        log_state(103u, off_function, already_off, simple_already_off);
        return;
    }
    g2_codec_power_state = 0u;
    (void)g2_codec_gpio_write(6u, 0u, 0u, 0u);
    (void)g2_codec_gpio_write(7u, 0u, 0u, 0u);
    (void)g2_codec_gpio_write(8u, 0u, 0u, 0u);
    log_state(110u, off_function, powered_off, simple_powered_off);
}
