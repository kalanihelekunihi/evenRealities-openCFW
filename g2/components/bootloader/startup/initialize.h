/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_INITIALIZE_H
#define OPENCFW_BOOT_INITIALIZE_H
#include <stdint.h>
uint32_t *opencfw_boot_expand_record(uint32_t *record,uint32_t static_base);
uint32_t *opencfw_boot_zero_table(uint32_t *table,uint32_t static_base);
#endif
