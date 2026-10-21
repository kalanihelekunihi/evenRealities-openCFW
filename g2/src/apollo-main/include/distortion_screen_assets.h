#ifndef OPENCFW_DISTORTION_SCREEN_ASSETS_H
#define OPENCFW_DISTORTION_SCREEN_ASSETS_H

#include <stdint.h>

/* Authenticated 28-byte LV image descriptor at stock 0x00769f58. */
struct distortion_screen_asset {
    uint32_t format;
    uint16_t width;
    uint16_t height;
    uint32_t stride;
    uint32_t pixel_bytes;
    const uint8_t *pixels;
    uint32_t reserved_0;
    uint32_t reserved_1;
};

extern const struct distortion_screen_asset audio_uart_distortion_asset_769f58;
extern const uint8_t audio_uart_distortion_text_736af4[];
extern const uint8_t audio_uart_distortion_text_736b24[];
extern uint32_t audio_uart_distortion_root_2007487c;

#endif
