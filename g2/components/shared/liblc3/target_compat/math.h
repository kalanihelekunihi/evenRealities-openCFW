/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Declaration-only freestanding math boundary for compiling the authenticated
 * liblc3 snapshot with a bare Clang arm-none-eabi toolchain.  These declarations
 * do not provide the target math implementations; that link/runtime provider is
 * an explicit integration seam.
 */

#ifndef OPEN_CFW_LIBLC3_TARGET_COMPAT_MATH_H
#define OPEN_CFW_LIBLC3_TARGET_COMPAT_MATH_H

#ifdef __cplusplus
extern "C" {
#endif

float fabsf(float value);
float floorf(float value);
float fmaxf(float first, float second);
float fminf(float first, float second);
float log10f(float value);
float log2f(float value);
float roundf(float value);
float sqrtf(float value);
float truncf(float value);

#ifdef __cplusplus
}
#endif

#endif
