/* Native Conversate tag icon mapper, 0x5b0af6..0x5b0b57. */
#include <stdint.h>

extern uintptr_t audio_conversate_tag_icon_map_2000052c[5];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_get_button_img";
static const char invalid[] = "Invalid tag type: %d";
static const char invalid_short[] = "[conversate.ui]Invalid tag type: %d";

uint32_t audio_conversate_tag_icon_get_5b0af6(uint32_t type) {
    if (type > 0u && type < 5u)
        return (uint32_t)audio_conversate_tag_icon_map_2000052c[type];
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source, function, 0x2cu, invalid, type);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, invalid_short,
                                    invalid_short, type);
    return 0u;
}
