/* Native conversate_ui_deinit 0x5b156c..0x5b15c3. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_conversate_ui_state_20071368[] __asm__("audio_conversate_ui_state_20071368");

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_conversate_ui_deinit_child_5b3d04(void);
extern void audio_terminal_ui_stop_voice_5896b4(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_deinit";
static const char message[] = "deinit completed";
static const char short_message[] = "[conversate.ui]deinit completed";

void audio_conversate_ui_exit_finalize_5b156c(void) {
    audio_uart_buffer_zero((void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_conversate_ui_state_20071368), 0xacu, 0u);
    audio_conversate_ui_deinit_child_5b3d04();
    audio_terminal_ui_stop_voice_5896b4();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 437u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
}
