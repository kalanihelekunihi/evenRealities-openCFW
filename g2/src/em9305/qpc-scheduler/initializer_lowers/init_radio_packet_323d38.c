#include <stdint.h>
#include <stddef.h>
/* Native 323d38..323d6e. Keep fresh byte reads in native store order,
 * including output/input overlap. Input byte 1 is intentionally unused. */
uint32_t opencfw_em9305_child_323d38(uintptr_t output, uintptr_t input)
{
    volatile uint8_t *out = (volatile uint8_t *)output;
    const volatile uint8_t *in = (const volatile uint8_t *)input;
    out[0] = 0u;
    out[1] = in[0];
    for (size_t i = 2u; i < 12u; ++i) out[i] = in[i];
    return 12u;
}
