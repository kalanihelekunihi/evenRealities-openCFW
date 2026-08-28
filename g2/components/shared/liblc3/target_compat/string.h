/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Declaration-only freestanding memory boundary used to compile liblc3 with a
 * bare arm-none-eabi Clang.  OpenCFW must bind these calls to reviewed target
 * providers when the candidate is linked.
 */

#ifndef OPEN_CFW_LIBLC3_TARGET_COMPAT_STRING_H
#define OPEN_CFW_LIBLC3_TARGET_COMPAT_STRING_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

void *memcpy(void *destination, const void *source, size_t count);
void *memmove(void *destination, const void *source, size_t count);
void *memset(void *destination, int value, size_t count);

#ifdef __cplusplus
}
#endif

#endif
