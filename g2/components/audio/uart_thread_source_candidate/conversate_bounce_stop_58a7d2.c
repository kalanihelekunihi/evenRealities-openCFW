/* Apollo Main bounce_animation_stop, native 0x58a7d2..0x58a83d. */
#include <stdint.h>

/* Native state begins at 0x20073e14, directly after the 16-byte CSF block.
 * The final linker script must establish that placement and non-overlap. */
volatile uint8_t audio_conversate_bounce_state_20073e14[16];

extern void audio_uart_page_43f142(uint32_t, int32_t);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "bounce.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\bounce_anim.c";
static const char function[] = "bounce_animation_stop";
static const char message[] = "Bounce animation stopped for obj=%p";
static const char compact[] = "[bounce.anim]Bounce animation stopped for obj=%p";

void audio_conversate_bounce_stop_58a7d2(uint32_t object) {
    if (object == 0u) return;
    volatile uint32_t *const state =
        (volatile uint32_t *)(void *)audio_conversate_bounce_state_20073e14;
    if (state[0] == object) {
        audio_uart_page_43f142(object, (int32_t)state[1]);
        state[0] = 0u;
    }
    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)object, 0);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0xe2u, message, object);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, compact, compact, object);
}
