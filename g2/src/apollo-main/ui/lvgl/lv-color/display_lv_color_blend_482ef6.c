/* Apollo LV RGB and alpha composition, native 0x482e4c..0x482f73. */
#include <stdint.h>

uint32_t audio_uart_lv_color_rgb_blend_482e4c(uint32_t foreground,
                                                uint32_t background) {
    uint32_t alpha = foreground >> 24u;
    if (alpha >= 0xfdu)
        return (background & 0xff000000u) | (foreground & 0x00ffffffu);
    if (alpha < 3u) return background;

    uint32_t result = background & 0xff000000u;
    for (unsigned shift = 0; shift < 24u; shift += 8u) {
        uint32_t first = (foreground >> shift) & 0xffu;
        uint32_t second = (background >> shift) & 0xffu;
        result |= (((first * alpha + second * (0xffu - alpha)) >> 8u) & 0xffu) << shift;
    }
    return result;
}

uint32_t audio_uart_lv_color_blend_482ef6(uint32_t foreground,
                                            uint32_t background) {
    uint32_t first_alpha = foreground >> 24u;
    uint32_t second_alpha = background >> 24u;
    if (first_alpha >= 0xfdu || second_alpha < 3u) return foreground;
    if (first_alpha < 3u) return background;
    if (second_alpha == 0xffu)
        return audio_uart_lv_color_rgb_blend_482e4c(foreground, background);

    uint32_t combined_alpha = 0xffu -
        (((0xffu - second_alpha) * (0xffu - first_alpha)) >> 8u);
    uint32_t normalized_alpha = (first_alpha * 0xffu) / (uint8_t)combined_alpha;
    uint32_t normalized_foreground = (foreground & 0x00ffffffu) |
                                     ((normalized_alpha & 0xffu) << 24u);
    uint32_t blended = audio_uart_lv_color_rgb_blend_482e4c(normalized_foreground,
                                                               background);
    return (blended & 0x00ffffffu) | ((combined_alpha & 0xffu) << 24u);
}
