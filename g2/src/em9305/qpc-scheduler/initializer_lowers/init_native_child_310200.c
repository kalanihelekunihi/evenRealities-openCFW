#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x310200..0x310230: clamp a signed power level. The upper bound
 * is the smaller of the radio status (query 1) and the signed limit byte at
 * (uintptr_t)&em9305_ram_8012b8; a level above it returns the bound, otherwise the level is
 * raised to at least the signed floor byte at ((uintptr_t)&em9305_ram_8012b8 + 0x1u). */
extern uint32_t opencfw_em9305_radio_status_311a00(uint32_t query);

int32_t opencfw_em9305_child_310200(int32_t level)
{
    int32_t status = (int32_t)opencfw_em9305_radio_status_311a00(1u);
    int32_t limit = em9305_ram_8012b8.s8_8012b8;
    int32_t upper = limit < status ? limit : status;
    if (upper < level) return upper;
    int32_t floor = em9305_ram_8012b8.s8_8012b9;
    return floor > level ? floor : level;
}
