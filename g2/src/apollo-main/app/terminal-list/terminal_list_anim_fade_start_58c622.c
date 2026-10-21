/* Stock common_button_fade_in/out_animation, 0x58c622 and 0x58c6c4. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_terminal_button_fade_callback_58c230(void);
extern void audio_uart_lv_anim_path_450688(void);

static const char module[] = "fade.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\fade_anim.c";
static const char function[] = "common_button_fade_in_animation";
static const char invalid[] =
    "common_button_fade_in_animation: obj is not valid";
static const char invalid_short[] =
    "[fade.anim]common_button_fade_in_animation: obj is not valid";

static void write_word(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

static void start(uint32_t object, uint32_t duration, uint32_t complete,
                  int32_t first, int32_t last) {
    (void)audio_uart_lv_style_unlink_450500(
        (void *)(uintptr_t)object,
        (void *)(uintptr_t)&audio_terminal_button_fade_callback_58c230);
    if (duration == 0u)
        duration = 250u;
    uint8_t descriptor[0x60];
    audio_uart_lv_anim_init_4503d6(descriptor);
    write_word(descriptor, 0u, object);
    audio_uart_lv_anim_values_4506ce(descriptor, first, last);
    write_word(descriptor, 0x30u, duration);
    write_word(descriptor, 4u,
               (uint32_t)(uintptr_t)&audio_terminal_button_fade_callback_58c230);
    write_word(descriptor, 0x20u,
               (uint32_t)(uintptr_t)&audio_uart_lv_anim_path_450688);
    if (complete != 0u)
        write_word(descriptor, 0x10u, complete);
    (void)audio_uart_lv_anim_start_450408(descriptor);
}

void audio_terminal_list_anim_new_start_58c622(uint32_t object,
                                                uint32_t duration,
                                                uint32_t complete) {
    if (object != 0u) {
        start(object, duration, complete, 0, 255);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 0x11au, invalid);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04000000u, invalid_short,
                                    invalid_short);
}

void audio_terminal_list_anim_old_start_58c6c4(uint32_t object,
                                                uint32_t duration,
                                                uint32_t complete) {
    if (object != 0u)
        start(object, duration, complete, 255, 0);
}
