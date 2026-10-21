/* Stock LVGL object-class ancestry query, 0x43e2d4..0x43e2e9. */
#include <stdint.h>

uint32_t audio_uart_lv_class_is_43e2d4(const void *object,
                                        const void *requested_class) {
    const void *klass = *(const void *const *)object;
    while (klass != 0) {
        if (klass == requested_class)
            return 1u;
        klass = *(const void *const *)klass;
    }
    return 0u;
}
