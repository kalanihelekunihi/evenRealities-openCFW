/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_CONTEXT_CLAIM_H
#define OPENCFW_BOOT_CONTEXT_CLAIM_H
#include <stdint.h>
#define OPENCFW_IOM_CONTEXT_COUNT 8u
#define OPENCFW_IOM_CONTEXT_BYTES 0x8a8u
/* Only the prefix and transaction snapshot offsets are recovered here.
 * The opaque tail is storage, not executable firmware or a complete layout. */
struct opencfw_iom_context {
    volatile uint32_t flags;
    volatile uint32_t module;
    volatile uint8_t opaque[OPENCFW_IOM_CONTEXT_BYTES - 8u];
};
extern struct opencfw_iom_context opencfw_boot_iom_contexts[8];
uint32_t opencfw_boot_context_claim(uint32_t module, uint32_t *output);
uint32_t opencfw_boot_context_transaction(struct opencfw_iom_context *handle,
                                         uint32_t command, uint32_t retain);
struct opencfw_iom_instance_config {
    uint8_t interface, pad0[3];
    uint32_t clock_hz;
    uint8_t spi_mode, pad1[3];
    uint32_t queue_buffer, queue_words;
};
uint32_t opencfw_boot_context_configure(struct opencfw_iom_context *,
    const struct opencfw_iom_instance_config *);
uint32_t opencfw_boot_context_enable(struct opencfw_iom_context *);
uint32_t opencfw_boot_context_retry(uint32_t index);
uint64_t opencfw_boot_iom_clock_config(uint32_t hz,uint32_t phase);
uint32_t opencfw_boot_iom_cq_initialize(void *,uint32_t words,uint32_t buffer);
uint32_t opencfw_boot_iom_cq_enable(void *);
uint32_t opencfw_boot_iom_cq_disable(void *);
#endif
