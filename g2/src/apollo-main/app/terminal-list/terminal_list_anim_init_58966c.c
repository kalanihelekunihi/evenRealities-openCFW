/* Stock list_anim_init 0x58966c, called by Terminal UI start. */
#include <stdint.h>

extern uint8_t audio_terminal_list_anim_state_base[0xd0]; /* RAM 0x20070ea8 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "list_anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\list_anim.c";
static const char function[] = "list_anim_init";
static const char message[] = "List animation manager initialized";
static const char short_message[] =
    "[list_anim]List animation manager initialized";

void audio_terminal_list_anim_init_58966c(void) {
    audio_uart_buffer_zero(audio_terminal_list_anim_state_base, 0xd0u, 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0xd0u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, short_message, short_message);
}
