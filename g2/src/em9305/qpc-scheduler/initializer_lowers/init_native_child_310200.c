#include <stdint.h>

/* Native 0x310200..0x310230: clamp a signed power level. The upper bound
 * is the smaller of the radio status (query 1) and the signed limit byte at
 * 0x8012b8; a level above it returns the bound, otherwise the level is
 * raised to at least the signed floor byte at 0x8012b9. */
extern uint32_t opencfw_em9305_radio_status_311a00(uint32_t query);

int32_t opencfw_em9305_child_310200(int32_t level)
{
    int32_t status = (int32_t)opencfw_em9305_radio_status_311a00(1u);
    int32_t limit = *(volatile int8_t *)(uintptr_t)0x8012b8u;
    int32_t upper = limit < status ? limit : status;
    if (upper < level) return upper;
    int32_t floor = *(volatile int8_t *)(uintptr_t)0x8012b9u;
    return floor > level ? floor : level;
}
