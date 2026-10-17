/* Apollo Main Conversate tag head reset 0x5969a4..0x596a29. */
#include <stdint.h>

extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.tag";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_set_auto_disp_node_to_head";
static const char missing[] = "Storage not initialized";
static const char missing_compact[] = "[conversate.tag]Storage not initialized";
static const char success[] = "Auto disp node set to head";
static const char success_compact[] = "[conversate.tag]Auto disp node set to head";

void audio_conversate_tag_unselect_5969a4(void) {
    volatile uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x1b8u, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u, missing_compact, missing_compact);
        return;
    }
    *(volatile uint32_t *)(void *)(state + 4u) =
        *(const volatile uint32_t *)(const void *)state;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x1bdu, success);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10000000u, success_compact, success_compact);
}
