#include <stdint.h>

/* Native 0x320dd8..0x320dfe: decode the incoming command into an 8-byte
 * result and, unless its status byte is 7 or 9, pass record and command
 * on to 320978. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t result, uintptr_t command);
extern uint32_t opencfw_em9305_child_320978(uintptr_t record, uintptr_t command);

uint32_t opencfw_em9305_child_320dd8(uintptr_t record, uintptr_t command)
{
    uint8_t result[8];
    (void)opencfw_em9305_dispatch_child_32db0c((uintptr_t)result,command);
    uint32_t status=result[0];
    if(status==7u||status==9u)return 0u;
    return opencfw_em9305_child_320978(record,command);
}
