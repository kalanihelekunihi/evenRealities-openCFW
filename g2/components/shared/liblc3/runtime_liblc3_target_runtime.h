/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LIBLC3_TARGET_RUNTIME_H
#define OPEN_CFW_LIBLC3_TARGET_RUNTIME_H

typedef __SIZE_TYPE__ open_cfw_liblc3_size_t;

void __aeabi_memclr(void *destination, open_cfw_liblc3_size_t size);
void __aeabi_memclr4(void *destination, open_cfw_liblc3_size_t size);
void *memcpy(void *destination, const void *source, open_cfw_liblc3_size_t size);
void *memmove(void *destination, const void *source, open_cfw_liblc3_size_t size);
void *memset(void *destination, int value, open_cfw_liblc3_size_t size);
float fabsf(float value);
float floorf(float value);
float fmaxf(float first, float second);
float fminf(float first, float second);
float truncf(float value);

#endif
