#include <stdint.h>

extern uint32_t case_mask_save(void);
extern void case_mask_restore(uint32_t before);

/* Original 0x0800c4cc..0x0800c4de. */
uint32_t xEventGroupGetBitsFromISR(void *event_group)
{
    const uint32_t before = case_mask_save();
    const uint32_t bits = *(volatile uint32_t *)event_group;
    case_mask_restore(before);
    return bits;
}
