/* SPDX-License-Identifier: MIT
 * Backup 0x1000e314. Field offsets are observed, not a complete state type.
 * All arithmetic is unsigned modulo 2^32, including workspace overflow.
 */
#include <stdint.h>
uint32_t open_cfw_gx8002_backup_imcra_workspace(const volatile uint32_t *state,
                                               uint32_t mode)
{
    uint32_t frame = state[3];
    uint32_t hop = state[5];
    uint32_t transform = state[4];
    uint32_t bins = state[7];
    uint32_t history = state[26];
    uint32_t extra = state[29];
    if (!mode) return 0;
    /* Preserve the reads above even though hop cancels algebraically. */
    return bins * 72u + bins * history * 8u + frame * 2u
         + (hop + frame + transform + (frame - hop) + extra * 2u + 1u) * 4u;
}
