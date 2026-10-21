/* SPDX-License-Identifier: MIT
 * NOR MSPI command queue uses stock Thumb 0x4222f1 dispatcher.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_clock_request(uint32_t clock,
    uint32_t user)
{
    __asm__ volatile("b.w clock_request");
}
