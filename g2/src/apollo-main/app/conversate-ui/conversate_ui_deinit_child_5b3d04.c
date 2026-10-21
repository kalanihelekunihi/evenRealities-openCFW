/* Native conversate_timer_mgr_deinit 0x5b3d04..0x5b3d61. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_conversate_timer_remove_5b36be(uint32_t, uint32_t);
extern void audio_conversate_timer_clear_5b38cc(void);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_mgr_deinit";
static const char message[] = "Timer manager deinitialized";
static const char short_message[] =
    "[conversate.timer]Timer manager deinitialized";

void audio_conversate_ui_deinit_child_5b3d04(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 382u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
    for (uint32_t index = 1u; index < 4u; ++index)
        audio_conversate_timer_remove_5b36be(index, 2u);
    audio_conversate_timer_clear_5b38cc();
}
