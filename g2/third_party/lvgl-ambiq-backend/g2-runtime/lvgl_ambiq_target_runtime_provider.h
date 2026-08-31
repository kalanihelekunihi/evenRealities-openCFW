/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_TARGET_RUNTIME_PROVIDER_H
#define OPENCFW_LVGL_AMBIQ_TARGET_RUNTIME_PROVIDER_H

#include <stddef.h>
#include <stdint.h>

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AEABI_BASE_PCS __attribute__((pcs("aapcs")))
#else
#define OPEN_CFW_AEABI_BASE_PCS
#endif

void * memcpy(void * destination, const void * source, size_t length);
void * memset(void * destination, int value, size_t length);
void __aeabi_memcpy4(void * destination, const void * source, size_t length);
OPEN_CFW_AEABI_BASE_PCS int64_t __aeabi_d2lz(double value);
OPEN_CFW_AEABI_BASE_PCS uint64_t __aeabi_f2ulz(float value);

#endif /* OPENCFW_LVGL_AMBIQ_TARGET_RUNTIME_PROVIDER_H */
