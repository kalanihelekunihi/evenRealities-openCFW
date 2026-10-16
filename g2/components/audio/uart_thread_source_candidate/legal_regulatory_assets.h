/* Authenticated LegalRegulatory resources and stock pointer-row order. */
#ifndef OPENCFW_LEGAL_REGULATORY_ASSETS_H
#define OPENCFW_LEGAL_REGULATORY_ASSETS_H
#include <stdint.h>
struct legal_regulatory_image {
    uint32_t format;
    uint16_t width;
    uint16_t height;
    uint32_t stride;
    uint32_t pixel_bytes;
    const uint8_t *pixels;
    uint32_t reserved_0;
    uint32_t reserved_1;
};
extern const void *const audio_legal_asset_slots[38];
#endif
