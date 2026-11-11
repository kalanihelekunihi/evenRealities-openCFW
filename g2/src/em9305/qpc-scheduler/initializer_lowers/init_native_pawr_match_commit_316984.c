#include <stdint.h>

/* Native 0x316984..0x3169b4: PAwR match commit. When the record is armed
 * (+64), step the ring index +66 backwards (0 wraps to 7), clear +65, mark the
 * slot in the bitmap +68 and store the (first, second) pair in slot
 * record+index*8. Returns the record. */
uintptr_t opencfw_em9305_pawr_match_commit_316984(uintptr_t record, uint32_t first, uint32_t second)
{
    if (*(volatile uint8_t *)(record + 64u) == 0u) return record;
    uint32_t index = *(volatile uint8_t *)(record + 66u);
    uint32_t bitmap = *(volatile uint32_t *)(record + 68u);
    *(volatile uint8_t *)(record + 65u) = 0u;
    index = index == 0u ? 7u : index - 1u;
    *(volatile uint8_t *)(record + 66u) = (uint8_t)index;
    bitmap |= 1u << (index & 31u);
    *(volatile uint32_t *)(record + 68u) = bitmap;
    *(volatile uint32_t *)(record + index * 8u + 4u) = second;
    *(volatile uint32_t *)(record + index * 8u) = first;
    return record;
}
