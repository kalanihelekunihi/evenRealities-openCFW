#include <stdint.h>

#define OPEN_CFW_SELECTOR 1
#include "../../components/apollo_main/core_overlay/opt3007_registers.c"

uint32_t host_opt3007_fill(uint8_t *destination)
{
    uint32_t index;
    uint32_t digest = 2166136261u;
    open_cfw_opt3007_assign_register_map(
        (open_cfw_opt3007_field *)(void *)destination);
    for (index = 0u; index < 57u; ++index) {
        digest = (digest ^ destination[index]) * 16777619u;
    }
    return digest;
}

void host_opt3007_null(void)
{
    open_cfw_opt3007_assign_register_map((open_cfw_opt3007_field *)0);
}
