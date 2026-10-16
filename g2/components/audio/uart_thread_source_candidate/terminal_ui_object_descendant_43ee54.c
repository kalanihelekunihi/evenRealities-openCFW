/* Stock LVGL object descendant check 0x43ee54. */
#include <stdint.h>

uint32_t audio_terminal_ui_object_descendant_43ee54(void *parent,
                                                      void *target) {
    uint8_t *const object = (uint8_t *)parent;
    uint8_t *const spec = (uint8_t *)(uintptr_t)
        *(uint32_t *)(void *)(object + 8u);
    if (spec == 0)
        return 0u;
    uint32_t count = *(uint16_t *)(void *)(spec + 0x30u);
    uint32_t *children = (uint32_t *)(uintptr_t)*(uint32_t *)(void *)spec;
    for (uint32_t i = 0u; i < count; ++i) {
        void *child = (void *)(uintptr_t)children[i];
        if (child == target ||
            (uint8_t)audio_terminal_ui_object_descendant_43ee54(child, target) != 0u)
            return 1u;
    }
    return 0u;
}
