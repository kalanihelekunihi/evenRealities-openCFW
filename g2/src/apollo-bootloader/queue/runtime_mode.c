/* SPDX-License-Identifier: MIT
 * Reconstructed 0x418B56..0x418B76 state query. Names are intentionally raw:
 * upstream kernel revision and semantic ownership of these words are unknown.
 */
#include <stdint.h>
uint32_t opencfw_bl_queue_runtime_mode(void)
{
    if (*(volatile uint32_t *)(uintptr_t)0x20027150u == 0u)
        return 1u;
    if (*(volatile uint32_t *)(uintptr_t)0x2002716cu == 0u)
        return 2u;
    return 0u;
}
