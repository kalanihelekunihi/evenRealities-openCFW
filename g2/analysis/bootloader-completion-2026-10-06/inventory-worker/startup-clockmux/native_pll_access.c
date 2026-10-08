/* Test-only accessors for the private static PLL-power leaves. Compile this
 * translation unit as source, not as an image/opcode substitute. */
#include "../../../../components/bootloader/clock_manager/clock_class_provider6.c"

void opencfw_test_syspll_power_initialize(void)
{
    pll_power_initialize();
}

void opencfw_test_syspll_power_restore(void)
{
    pll_power_restore();
}
