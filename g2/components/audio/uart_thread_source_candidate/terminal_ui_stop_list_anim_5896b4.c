/* Stock list_anim_deinit 0x5896b4, called first by terminal teardown.
 * The exported name follows the existing terminal child frontier. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

uint8_t audio_terminal_list_anim_state_base[0xd0]
    __attribute__((section(".bss.opencfw.terminal.list_anim_state"), aligned(4), used));
_Static_assert(sizeof audio_terminal_list_anim_state_base == 0xd0u,
               "stock list animation clear extent");

static const char module[] = "list_anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\list_anim.c";
static const char function[] = "list_anim_deinit";
static const char message[] = "List animation manager deinitialized";
static const char short_message[] =
    "[list_anim]List animation manager deinitialized";

void audio_terminal_ui_stop_voice_5896b4(void) {
    audio_uart_buffer_zero(audio_terminal_list_anim_state_base, 0xd0u, 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0xdau, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, short_message, short_message);
}
