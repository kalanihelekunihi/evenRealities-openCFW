#include "init_lower_native.h"

extern uint8_t *const opencfw_em9305_ext_init_records_3357a8[3];
extern uint8_t *const opencfw_em9305_stream_objects_3357b4[3];

/* Native 0x307a18..0x307a24 and 0x307b60..0x307b6c. Tables are
 * the source-owned symbols (wave 26: were raw stock addresses 0x3357a8/0x3357b4). ARC ld.as indexes a word table with index*4. */
uint32_t opencfw_em9305_callback_307a18(uint32_t index)
{
    uintptr_t context = (uintptr_t)opencfw_em9305_ext_init_records_3357a8[index];
    return init_read8(context) != 0u;
}

uint32_t opencfw_em9305_callback_307b60(uint32_t index)
{
    uintptr_t context = (uintptr_t)opencfw_em9305_stream_objects_3357b4[index];
    return init_read8(context) != 0u;
}
