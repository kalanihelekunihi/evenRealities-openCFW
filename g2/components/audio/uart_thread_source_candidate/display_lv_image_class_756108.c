/* Stock LVGL image class record 0x756108..0x75612b. */
#include <stdint.h>

extern const uint8_t audio_uart_lv_base_class_7564f8[];
extern void audio_uart_lv_image_ctor_498bd0(void);
extern void audio_uart_lv_image_dtor_498c6c(void);
extern void audio_uart_lv_image_event_498c9c(void);

struct audio_uart_lv_image_class_layout {
    uintptr_t base_class;
    uintptr_t constructor;
    uintptr_t destructor;
    uintptr_t event;
    uint32_t reserved;
    uintptr_t name;
    uint32_t default_width;
    uint32_t default_height;
    uint32_t instance_size;
};

_Static_assert(sizeof(struct audio_uart_lv_image_class_layout) == 36u,
               "Apollo LVGL image class record size");

const char audio_uart_lv_image_class_name_78b33c[] = "lv_image";

const struct audio_uart_lv_image_class_layout audio_uart_image_class_756108 = {
    (uintptr_t)audio_uart_lv_base_class_7564f8,
    (uintptr_t)&audio_uart_lv_image_ctor_498bd0,
    (uintptr_t)&audio_uart_lv_image_dtor_498c6c,
    (uintptr_t)&audio_uart_lv_image_event_498c9c,
    0u,
    (uintptr_t)audio_uart_lv_image_class_name_78b33c,
    0x3fffffffu,
    0x3fffffffu,
    0x5c0u,
};
