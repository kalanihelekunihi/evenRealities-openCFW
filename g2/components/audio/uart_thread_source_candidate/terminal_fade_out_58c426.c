/* Stock common_fade_out_animation at 0x58c426. */
#include <stdint.h>

extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_legal_regulatory_fade_callback_58c12c(void);
extern void audio_uart_lv_anim_path_450672(void);

static const char module[] = "fade.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\fade_anim.c";
static const char function[] = "common_fade_out_animation";
static const char invalid[] = "common_fade_out_animation: obj is not valid";
static const char invalid_short[] =
    "[fade.anim]common_fade_out_animation: obj is not valid";
static const char started[] = "fade out animation started";
static const char started_short[] =
    "[fade.anim]fade out animation started";

static void log_event(uint8_t level, uint32_t line, uint32_t mask,
                      const char *plain, const char *compact) {
    if (audio_log_level() & 2u)
        audio_log_extended(level, module, path, function, line, plain);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(mask, compact, compact);
}

static void write_word(uint8_t *bytes, uint32_t offset, uintptr_t value) {
    *(uint32_t *)(void *)(bytes + offset) = (uint32_t)value;
}

void audio_terminal_fade_out_58c426(uint32_t object, uint32_t duration,
                                     void (*complete)(void)) {
    if (object == 0u) {
        log_event(1u, 0xbau, 0x04000000u, invalid, invalid_short);
        return;
    }
    (void)audio_uart_lv_style_unlink_450500(
        (void *)(uintptr_t)object,
        (void *)(uintptr_t)audio_legal_regulatory_fade_callback_58c12c);
    if (duration == 0u)
        duration = 0xfau;
    uint8_t animation[0x60];
    audio_uart_lv_anim_init_4503d6(animation);
    write_word(animation, 0u, object);
    audio_uart_lv_anim_values_4506ce(animation, 0xff, 0);
    write_word(animation, 4u,
               (uintptr_t)audio_legal_regulatory_fade_callback_58c12c);
    write_word(animation, 0x20u,
               (uintptr_t)audio_uart_lv_anim_path_450672);
    if (complete != 0)
        write_word(animation, 0x10u, (uintptr_t)complete);
    write_word(animation, 0x30u, duration);
    (void)audio_uart_lv_anim_start_450408(animation);
    log_event(4u, 0xcau, 0x10000000u, started, started_short);
}
