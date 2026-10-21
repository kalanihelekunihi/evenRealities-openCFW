/* Apollo LV base class, stock ROM 0x7564f8..0x75651b. */
#include <stdint.h>

extern void audio_uart_lv_base_ctor_43e33e(void *, void *);
extern void audio_uart_lv_base_dtor_43e3de(void *, void *);
extern void audio_uart_lv_base_event_43e7d2(void *, void *);

struct audio_uart_lv_base_class_layout {
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

_Static_assert(sizeof(struct audio_uart_lv_base_class_layout) == 36u,
               "Apollo LV base class record size");

const char audio_uart_lv_base_class_name_78dc64[] = "lv_obj";

const struct audio_uart_lv_base_class_layout audio_uart_lv_base_class_7564f8 = {
    0u,
    (uintptr_t)&audio_uart_lv_base_ctor_43e33e,
    (uintptr_t)&audio_uart_lv_base_dtor_43e3de,
    (uintptr_t)&audio_uart_lv_base_event_43e7d2,
    0u,
    (uintptr_t)audio_uart_lv_base_class_name_78dc64,
    0x82u,
    0x82u,
    0x2cau,
};
