#ifndef OPENCFW_TERMINAL_RESET_ASSETS_20261016_H
#define OPENCFW_TERMINAL_RESET_ASSETS_20261016_H
#include <stdint.h>
struct terminal_reset_image_asset {
    uint32_t format;
    uint16_t width;
    uint16_t height;
    uint32_t stride;
    uint32_t pixel_bytes;
    const uint8_t *pixels;
    uint32_t reserved_0;
    uint32_t reserved_1;
};
_Static_assert(sizeof(struct terminal_reset_image_asset) == 28u, "LV image descriptor extent");
extern const struct terminal_reset_image_asset audio_terminal_asset_773028;
extern const struct terminal_reset_image_asset audio_terminal_asset_7733a8;
extern const uint8_t audio_terminal_welcome_text_7069d0[68];
#endif
