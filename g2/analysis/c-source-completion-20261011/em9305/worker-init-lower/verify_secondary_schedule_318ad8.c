#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t,uint32_t);
int main(void)
{
    uint8_t connection[280];
    memset(connection,0,sizeof connection);
    *(uint16_t *)(void *)(connection+266u)=2u;
    *(uint16_t *)(void *)(connection+262u)=30u;
    *(uint32_t *)(void *)(connection+24u)=100000u;
    assert(opencfw_em9305_init_secondary_schedule_318ad8(
        (uintptr_t)connection,34u)==110000u);
    assert(opencfw_em9305_init_secondary_schedule_318ad8(
        (uintptr_t)connection,26u)==90000u);
    connection[2]=1u;
    *(uint16_t *)(void *)(connection+202u)=51u;
    *(uint32_t *)(void *)(connection+208u)=200000u;
    assert(opencfw_em9305_init_secondary_schedule_318ad8(
        (uintptr_t)connection,54u)==210000u);
    assert(opencfw_em9305_init_secondary_schedule_318ad8(
        (uintptr_t)connection,46u)==190000u);
    return 0;
}
