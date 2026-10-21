/* Native 0x1000d1fc: assign IMCRA work-buffer regions in stock order.
 * ctx is word aligned as in the native call graph. Arithmetic wraps in
 * target 32-bit registers, so addresses are represented as uint32_t.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);

void gx8002_image_b_imcra_layout_1000d1fc(uint32_t *ctx, uint32_t base)
{
    uint32_t channels = ctx[0x08 / 4];
    uint32_t band_stride = ctx[0x04 / 4];
    uint32_t history = ctx[0x0c / 4];
    uint32_t hop = ctx[0x10 / 4];
    uint32_t initial_offset = ctx[0x14 / 4];
    uint32_t bins = ctx[0x18 / 4];
    uint32_t count = ctx[0x1c / 4];
    (void)gx8002_image_b_heap_log_10009934("frequency_bins: %d\n", bins);

    uint32_t bin_bytes = channels * bins * 4u;
    uint32_t region = initial_offset * 2u + base;
    uint32_t band_count = band_stride * channels;
    ctx[0x78 / 4] = region;
    region += bin_bytes;
    ctx[0x84 / 4] = base;
    ctx[0x7c / 4] = region;
    region += bin_bytes;
    ctx[0x6c / 4] = region;
    region += band_count * 8u;
    ctx[0xcc / 4] = region;
    region += (band_count - channels) * 8u;
    uint32_t channel_bytes = channels * 8u;
    ctx[0xc8 / 4] = region;
    region += channel_bytes;
    ctx[0xd0 / 4] = region;
    region += channel_bytes;
    ctx[0x68 / 4] = region;
    region += channel_bytes;
    ctx[0x90 / 4] = region;
    region += bin_bytes;
    ctx[0x88 / 4] = region;
    region += (history + (channels - 1u) * hop) * 2u;
    ctx[0x80 / 4] = region;
    region += count * (history - hop) * 2u;
    ctx[0xa0 / 4] = region;
    region += bins * 4u;
    ctx[0x98 / 4] = region;
    ctx[0x9c / 4] = region + bins * 4u;
}
