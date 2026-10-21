/* Native conversate_tag_storage_init 0x59619e..0x59624d. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

__attribute__((used, section(".g2_conversate_tag_storage_200e3af4")))
uint8_t audio_conversate_tag_storage_state_200e3af4[12];

static const char module[] = "conversate.tag";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_storage_init";
static const char already[] = "Storage already initialized";
static const char already_short[] = "[conversate.tag]Storage already initialized";
static const char success[] =
    "Tag storage initialized successfully, unlimited capacity";
static const char success_short[] =
    "[conversate.tag]Tag storage initialized successfully, unlimited capacity";

uint32_t audio_conversate_tag_storage_init_59619e(void) {
    uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 147u, already);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, already_short, already_short);
        return 1u;
    }
    audio_uart_buffer_zero(state, 12u, 0u);
    state[0] = 0u;
    state[1] = 0u;
    state[2] = 0u;
    state[3] = 0u;
    state[8] = 0u;
    state[9] = 0u;
    state[10] = 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 158u, success);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, success_short, success_short);
    return 1u;
}
