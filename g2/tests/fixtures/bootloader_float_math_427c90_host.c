/* Host-only adapter for the freestanding G2 bootloader float helpers. */
#include "../../components/bootloader/core_overlay/runtime_float_math_427c90.c"
#include "../../components/bootloader/core_overlay/runtime_float_math_veneers_427c90.c"

open_cfw_u32 open_cfw_float_math_host_classify_bits(open_cfw_u32 bits)
{
    open_cfw_float_bits input;
    input.bits = bits;
    return open_cfw_bootloader_float_range_classify_427e0c(input.value);
}
