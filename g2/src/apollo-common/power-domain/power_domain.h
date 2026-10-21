/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_POWER_DOMAIN_H
#define OPENCFW_POWER_DOMAIN_H
#include <stdint.h>
/* Recovered 16-byte data records, not a hardware register abstraction. */
typedef struct {
    uint32_t enable_register, enable_mask, status_register, status_mask;
} opencfw_power_domain_descriptor_t;
uint32_t opencfw_power_domain_descriptor(opencfw_power_domain_descriptor_t *out, uint32_t domain);
/* Stock 55ca72 selects (uint8_t)(module+3); this only maps its descriptor. */
uint32_t opencfw_iom_domain_descriptor(opencfw_power_domain_descriptor_t *out, uint32_t module);
#endif
