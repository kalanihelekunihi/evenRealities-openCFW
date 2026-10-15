/* Apollo page class at stock ROM 0x7561bc..0x7561df.
 * Callback fields relocate to C bodies. Base-class/name ROM literals still
 * require source ownership before a complete firmware layout is possible. */
#include <stdint.h>

extern void audio_uart_page_class_ctor_49a0c0(void);
extern void audio_uart_page_class_dtor_49a150(void);
extern void audio_uart_page_class_event_49a16e(void);

struct audio_uart_page_class_layout {
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

_Static_assert(sizeof(struct audio_uart_page_class_layout) == 36u,
               "Apollo page class record size");

const struct audio_uart_page_class_layout audio_uart_page_class_7561bc = {
    (uintptr_t)0x007564f8u,
    (uintptr_t)&audio_uart_page_class_ctor_49a0c0,
    (uintptr_t)&audio_uart_page_class_dtor_49a150,
    (uintptr_t)&audio_uart_page_class_event_49a16e,
    0u,
    (uintptr_t)0x0078b390u,
    0x3fffffffu,
    0x3fffffffu,
    0x600u
};
