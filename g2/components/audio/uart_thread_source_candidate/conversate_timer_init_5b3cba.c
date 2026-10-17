/* Native conversate_timer_mgr_init 0x5b3cba..0x5b3d03. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern void audio_conversate_timer_clear_5b38cc(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_mgr_init";
static const char message[] = "Timer manager initialized";
static const char short_message[] =
    "[conversate.timer]Timer manager initialized";

void audio_conversate_timer_init_5b3cba(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    audio_conversate_timer_clear_5b38cc();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 373u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
}
