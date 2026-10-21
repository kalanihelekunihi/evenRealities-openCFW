/* Apollo Main LVGL animation speed conversion and descriptor normalization. */
#include <stdint.h>

uint32_t audio_uart_lv_anim_speed_to_time_4506fc(uint32_t packed,
                                                  int32_t start,
                                                  int32_t end) {
    if ((int32_t)packed >= 0) return packed;
    const int32_t difference = (int32_t)((uint32_t)start - (uint32_t)end);
    const uint32_t distance = (uint32_t)(difference > 0
        ? difference : (int32_t)((uint32_t)end - (uint32_t)start));
    const uint32_t divisor = packed & 0x3ffu;
    uint32_t duration = divisor == 0u ? 0u : (distance * 100u) / divisor;
    const uint32_t maximum = ((packed & 0x3fffffffu) >> 20) * 10u;
    const uint32_t minimum = ((packed & 0xfffffu) >> 10) * 10u;
    const uint32_t bounded = duration < maximum ? duration : maximum;
    if (bounded < minimum) duration = minimum;
    else if (maximum <= duration) duration = maximum;
    return duration;
}

void audio_uart_lv_anim_normalize_450a3e(void *descriptor) {
    uint8_t *const bytes = (uint8_t *)descriptor;
    const int32_t start = *(int32_t *)(void *)(bytes + 0x24u);
    const int32_t end = *(int32_t *)(void *)(bytes + 0x2cu);
    const uint32_t offsets[] = {0x30u, 0x3cu, 0x38u, 0x40u};
    for (uint32_t i = 0; i < 4u; ++i) {
        uint32_t *const field = (uint32_t *)(void *)(bytes + offsets[i]);
        *field = audio_uart_lv_anim_speed_to_time_4506fc(*field, start, end);
    }
}
