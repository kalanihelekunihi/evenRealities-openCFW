/* Stock audio hardware descriptor builder, 0x59123a. */
#include <stdint.h>

extern int32_t audio_app_rate_index_590d3c(int32_t, uint32_t);
extern uint32_t audio_app_format_index_590d74(int32_t, uint32_t);
extern void audio_uart_lv_memzero_48949c(void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_app_zero_tail_4d4ccc(void *, uint32_t);

static const int32_t channel_sizes[7] = {20, 40, 60, 80, 120, 120, 240};

static int32_t quotient_1000(int32_t value) {
    int64_t product = (int64_t)value * INT64_C(0x10624dd3);
    int32_t high = (int32_t)(product >> 32);
    int32_t shifted = high >> 6;
    return shifted + (int32_t)((uint32_t)shifted >> 31);
}

void *audio_app_hardware_core_59123a(uint32_t format, int32_t rate,
                                      int32_t first_channel, int32_t last_channel,
                                      void *output) {
    if (last_channel <= 0)
        last_channel = first_channel;
    int32_t rate_index = audio_app_rate_index_590d3c(rate, format);
    uint32_t first_index = audio_app_format_index_590d74(first_channel, format);
    uint32_t last_index = audio_app_format_index_590d74(last_channel, format);
    if (rate_index >= 4 || (int32_t)last_index >= 7 || last_index < first_index ||
        !output)
        return 0;

    int32_t size = channel_sizes[last_index];
    int32_t total = (int32_t)((uint32_t)(rate_index + 1) * (uint32_t)size);
    int32_t half = size >> 1;
    uint8_t descriptor[0x4b0];
    audio_uart_lv_memzero_48949c(descriptor, sizeof descriptor);
    int32_t middle = (int32_t)(((int64_t)half + total) / 2);
    descriptor[0] = (uint8_t)rate_index;
    descriptor[1] = (uint8_t)first_index;
    descriptor[2] = (uint8_t)last_index;
    *(int32_t *)(descriptor + 0x4a0u) = half;
    *(int32_t *)(descriptor + 0x4a4u) = middle;
    *(int32_t *)(descriptor + 0x4a8u) = total + middle;
    (void)audio_uart_display_area_copy_439c04(output, descriptor,
                                                sizeof descriptor);

    int32_t rate_x_last = (int32_t)((uint32_t)rate * (uint32_t)last_channel);
    int32_t base_x_last = (int32_t)(1250u * (uint32_t)last_channel);
    int32_t selected = rate == 7500 ? 2000 : 1250;
    int32_t selected_x_last = (int32_t)((uint32_t)selected *
                                         (uint32_t)last_channel);
    int32_t primary = quotient_1000(quotient_1000(rate_x_last));
    int32_t secondary = quotient_1000(quotient_1000(base_x_last));
    int32_t tertiary = quotient_1000(quotient_1000(selected_x_last));
    int32_t pair = secondary + primary;
    int32_t pair_half = (pair + (int32_t)((uint32_t)pair >> 31)) >> 1;
    int32_t primary_half =
        (primary + (int32_t)((uint32_t)primary >> 31)) >> 1;
    uint32_t tail = (uint32_t)(tertiary + primary + pair_half + primary_half) << 2;
    audio_app_zero_tail_4d4ccc((uint8_t *)output + 0x4acu, tail);
    return output;
}
