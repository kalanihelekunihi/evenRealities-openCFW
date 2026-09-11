static unsigned int open_cfw_test_mie_primask;
static unsigned int open_cfw_test_mie_enable_calls;

#define OPEN_CFW_BOOTLOADER_READ_PRIMASK_MIE() open_cfw_test_mie_primask
#define OPEN_CFW_BOOTLOADER_CPSIE_MIE() (open_cfw_test_mie_enable_calls += 1U)
#include "../../components/bootloader/core_overlay/runtime_master_interrupt_enable_41b8e0.c"

void open_cfw_test_mie_set(unsigned int primask)
{
    open_cfw_test_mie_primask = primask;
    open_cfw_test_mie_enable_calls = 0U;
}

unsigned int open_cfw_test_mie_enable_calls_made(void)
{
    return open_cfw_test_mie_enable_calls;
}
