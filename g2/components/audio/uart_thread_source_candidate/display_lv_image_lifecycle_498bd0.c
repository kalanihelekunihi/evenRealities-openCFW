/* Stock LVGL image constructor/destroyer, 0x498bd0 and 0x498c6c. */
#include <stdint.h>

extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_lv_object_clear_flag_43dfa4(uint32_t, uint32_t);
extern void audio_lv_object_call_43ded4(uint32_t, uint32_t);
extern void audio_uart_lv_heap_free(void *);

static uint32_t word(const uint8_t *object, uint32_t offset) {
    return *(const uint32_t *)(const void *)(object + offset);
}

static void store_word(uint8_t *object, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(object + offset) = value;
}

void audio_uart_lv_image_ctor_498bd0(const void *klass, void *instance) {
    (void)klass;
    uint8_t *object = (uint8_t *)instance;
    store_word(object, 0x2cu, 0u);
    uint32_t flags = word(object, 0x58u);
    flags = (flags | 3u) & ~0x7cu;
    store_word(object, 0x58u, flags);
    store_word(object, 0x3cu, (uint32_t)audio_uart_lv_obj_width_43fd9e(object));
    store_word(object, 0x40u, (uint32_t)audio_uart_lv_obj_height_43fdda(object));
    store_word(object, 0x44u, 0u);
    store_word(object, 0x48u, 0x100u);
    store_word(object, 0x4cu, 0x100u);
    flags = word(object, 0x58u) & ~0x80u;
    flags = (flags & ~0xf00u) | 0x900u;
    store_word(object, 0x58u, flags);
    store_word(object, 0x34u, 0u);
    store_word(object, 0x38u, 0u);
    /* LVGL encodes a 50 percent pivot as 0x20000032 on both axes. */
    store_word(object, 0x50u, 0x20000032u);
    store_word(object, 0x54u, 0x20000032u);
    audio_lv_object_clear_flag_43dfa4((uint32_t)(uintptr_t)object, 2u);
    audio_lv_object_call_43ded4((uint32_t)(uintptr_t)object, 0x10000u);
}

void audio_uart_lv_image_dtor_498c6c(const void *klass, void *instance) {
    (void)klass;
    uint8_t *object = (uint8_t *)instance;
    const uint32_t ownership = object[0x58u] & 3u;
    if (ownership == 1u || ownership == 2u) {
        audio_uart_lv_heap_free((void *)(uintptr_t)word(object, 0x2cu));
        store_word(object, 0x2cu, 0u);
        store_word(object, 0x58u, word(object, 0x58u) | 3u);
    }
}
