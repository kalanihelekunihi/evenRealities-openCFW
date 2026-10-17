/* Native conversate_get_tag_storage_count, 0x59674e..0x5967a5. */
#include <stdint.h>

extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.tag";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_get_tag_storage_count";
static const char uninitialized[] = "Storage not initialized";
static const char uninitialized_short[] =
    "[conversate.tag]Storage not initialized";

uint32_t audio_conversate_tag_storage_count_59674e(void) {
    const uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] != 0u)
        return *(const uint16_t *)(const void *)(state + 8u);
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source, function, 0x133u,
                           uninitialized);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04000000u, uninitialized_short,
                                    uninitialized_short);
    return 0u;
}
