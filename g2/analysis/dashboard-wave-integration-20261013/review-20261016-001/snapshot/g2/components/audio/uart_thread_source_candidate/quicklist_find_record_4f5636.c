/* Apollo QuickList record ID lookup at 0x4f5636..0x4f5661. */
#include <stdint.h>

int32_t audio_quicklist_find_record_4f5636(uint32_t id) {
    const volatile uint8_t *const rows = (const volatile uint8_t *)(uintptr_t)0x2012a72cu;
    const uint16_t count = *(const volatile uint16_t *)(const void *)rows;
    for (uint32_t index = 0u; index < count; ++index) {
        const uint32_t candidate = *(const volatile uint32_t *)(const void *)(
            rows + 296u * index + 0x114u);
        if (candidate == id)
            return (int32_t)index;
    }
    return -1;
}
