/* Apollo PageManager registration, stock 0x45f3c8..0x45f58a. */
#include <stdint.h>

extern uint32_t audio_uart_display_audio_unique_45fb44(void *, uint32_t);
extern void *codec_allocate(uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_display_audio_allocation_fatal_45f402(void);
extern void audio_uart_lv_obj_set_parent_44d94c(void *, void *);
extern void audio_uart_page_43ded4(void *, uint32_t);
extern void audio_uart_page_43f66c(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_page_43f0e0(void *, int32_t);
extern void audio_uart_page_43f142(void *, int32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

void *audio_uart_display_audio_enqueue_45f3c8(void *state, void *configuration) {
    if (state == 0 || configuration == 0) return 0;
    uint8_t *s = (uint8_t *)state;
    uint8_t *config = (uint8_t *)configuration;
    uint32_t id = get32(config);
    if (id == 0u || audio_uart_display_audio_unique_45fb44(state, id) == 0u)
        return 0;

    uint8_t *entry = (uint8_t *)codec_allocate(40u);
    if (entry == 0) {
        audio_uart_display_audio_allocation_fatal_45f402();
        return 0;
    }
    (void)audio_uart_display_area_copy_439c04(entry, config, 28u);
    if (get32(entry + 12u) == 0u) put32(entry + 12u, 300u);
    if (get32(entry + 16u) == 0u) put32(entry + 16u, 300u);
    if ((int16_t)(uint16_t)(entry[20] | ((uint16_t)entry[21] << 8u)) == 0) {
        entry[20] = 50u;
        entry[21] = 0u;
    }
    if (entry[22] == 0u) entry[22] = 100u;

    uint8_t *object = (uint8_t *)(uintptr_t)get32(config + 4u);
    uint8_t *parent = (uint8_t *)(uintptr_t)get32(s + (config[11] == 0u ? 28u : 32u));
    audio_uart_lv_obj_set_parent_44d94c(object, parent);
    if (config[11] == 0u) {
        if (config[23] != 0u) {
            entry[28] = 1u;
        } else {
            audio_uart_page_43ded4(object, 1u);
            entry[28] = 0u;
        }
    } else {
        audio_uart_page_43f66c(parent);
        if (config[8] == 0u)
            audio_uart_page_43f0e0(object, -audio_uart_lv_obj_width_43fd9e(object));
        else if (config[8] == 1u)
            audio_uart_page_43f142(object, audio_uart_lv_obj_height_43fdda(parent));
        else
            audio_uart_page_43f142(object, -audio_uart_lv_obj_height_43fdda(object));
        entry[28] = 0u;
    }
    put32(object + 16u, (uint32_t)(uintptr_t)entry);
    audio_uart_page_43ded4(object, 0x4000u);

    uint32_t list_offset = config[11] == 0u ? 12u : 8u;
    uint8_t *old_head = (uint8_t *)(uintptr_t)get32(s + list_offset);
    put32(entry + 32u, (uint32_t)(uintptr_t)old_head);
    put32(entry + 36u, 0u);
    if (old_head != 0) put32(old_head + 36u, (uint32_t)(uintptr_t)entry);
    put32(s + list_offset, (uint32_t)(uintptr_t)entry);
    if (list_offset == 12u && entry[28] == 1u)
        put32(s + 4u, (uint32_t)(uintptr_t)entry);
    return entry;
}
