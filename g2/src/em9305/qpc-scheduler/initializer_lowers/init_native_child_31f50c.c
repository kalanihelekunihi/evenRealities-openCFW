#include <stdint.h>

/* Native 0x31f50c..0x31f536: decode the incoming command into an 8-byte
 * result, latch its status byte at 0x803b68 and, unless the status is 7
 * or 9, continue with 31f86c on the record. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t result, uintptr_t command);
extern uint32_t opencfw_em9305_child_31f86c(uintptr_t record);

uint32_t opencfw_em9305_child_31f50c(uintptr_t record, uintptr_t command)
{
    uint8_t result[8];
    (void)opencfw_em9305_child_32db0c((uintptr_t)result,command);
    uint32_t status=result[0];
    *(volatile uint8_t *)(uintptr_t)0x803b68u=(uint8_t)status;
    if(status==7u||status==9u)return 0u;
    return opencfw_em9305_child_31f86c(record);
}
