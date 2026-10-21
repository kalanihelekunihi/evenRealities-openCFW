/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_IOM_RELEASE_H
#define OPENCFW_IOM_RELEASE_H
#include <stdint.h>
/* Stock sparse IOM view: prefix@0, module@4, pending@0x24, CQ pointer@0x828.
 * Callers supply mapped ARM32 storage; no allocator/initializer supplied. */
uint32_t opencfw_iom_cq_term(void *handle);
uint32_t opencfw_iom_disable(void *handle);
uint32_t opencfw_iom_uninitialize(void *handle);
#endif
