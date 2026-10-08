/* SPDX-License-Identifier: MIT. Reconstructed locked 0x42c4c6..0x42c538. */
#include "context_claim.h"
_Static_assert(sizeof(struct opencfw_iom_context) == 0x8a8u, "stock slot stride");
struct opencfw_iom_context opencfw_boot_iom_contexts[8]
    __attribute__((section(".bss.boot_iom_context_pool"), aligned(4)));
uint32_t opencfw_boot_context_claim(uint32_t module, uint32_t *output)
{
    if (module >= 8u) return 5u;
    if (output == 0) return 6u;
    struct opencfw_iom_context *const slot = &opencfw_boot_iom_contexts[module];
    if ((slot->flags & 0x01000000u) != 0u) return 7u;
    /* Preserve the three observable writes and unrelated upper flags. */
    slot->flags |= 0x01000000u;
    slot->flags &= ~0x02000000u;
    slot->flags = (slot->flags & 0xff000000u) | 0x00123456u;
    slot->module = module;
    *output = (uint32_t)(uintptr_t)slot;
    return 0u;
}
