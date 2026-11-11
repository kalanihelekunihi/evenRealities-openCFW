#include <stdint.h>

/* Native 0x31c500..0x31c52c: consume a pending parameter update. When the
 * pending byte +514 is set, copy bytes +512/+513 to +110/+111; mode 1 points
 * the +112 buffer slot at the record's inline area +262, any other mode
 * clears it. The pending byte is always cleared; the record is returned. */
uintptr_t opencfw_em9305_child_31c500(uintptr_t record)
{
    volatile uint8_t *pending = (volatile uint8_t *)(record + 512u);
    if (pending[2] != 0u) {
        uint8_t mode = pending[1];
        *(volatile uint8_t *)(record + 110u) = pending[0];
        *(volatile uint8_t *)(record + 111u) = mode;
        if (mode == 1u)
            *(volatile uint32_t *)(record + 112u) = (uint32_t)(record + 262u);
        else
            *(volatile uint32_t *)(record + 112u) = 0u;
    }
    pending[2] = 0u;
    return record;
}
