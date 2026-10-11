#include <stdint.h>

/* Native constant lookup bodies 0x539348, 0x539352, 0x53935c,
 * 0x539372. Their accepted source IDs are 0..15; these typed maps
 * transcribe authenticated read-only tables 0x784c40/50/60 and
 * 0x78c98c. The native entries do no range check on source IDs. */
static const uint8_t group_map[16] = {
    0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 0, 0
};
static const uint8_t setting_map[16] = {
    0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 0, 1, 2, 0, 0
};
static const uint8_t mask_map[16] = {
    0x10, 1, 0, 0x10, 1, 0, 0x10, 0,
    0x10, 0x10, 0, 0x10, 0x10, 0, 0, 0
};
static const uint8_t path_map[5] = { 2, 1, 5, 3, 4 };

uint8_t g2_clock_mux_group(uint8_t source) { return group_map[source]; }
uint8_t g2_clock_mux_setting(uint8_t source) { return setting_map[source]; }
uint8_t g2_clock_mux_mask(uint8_t source) { return mask_map[source]; }
uint8_t g2_clock_mux_path(uint8_t group) {
    return group < 5u ? path_map[group] : 6u;
}
