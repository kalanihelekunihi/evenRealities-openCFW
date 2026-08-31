/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_target_runtime_provider.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(size_t) == 4, "G2 size_t ABI changed");
_Static_assert(sizeof(double) == 8, "G2 binary64 ABI changed");
_Static_assert(sizeof(float) == 4, "G2 binary32 ABI changed");
_Static_assert(sizeof(int64_t) == 8, "G2 signed 64-bit ABI changed");
_Static_assert(sizeof(uint64_t) == 8, "G2 unsigned 64-bit ABI changed");

int64_t open_cfw_target_runtime_probe_d2lz(double value)
{
    return __aeabi_d2lz(value);
}

uint64_t open_cfw_target_runtime_probe_f2ulz(float value)
{
    return __aeabi_f2ulz(value);
}

void open_cfw_target_runtime_provider_abi_probe(void)
{
    void * (*copy)(void *, const void *, size_t) = memcpy;
    void * (*fill)(void *, int, size_t) = memset;
    void (*copy4)(void *, const void *, size_t) = __aeabi_memcpy4;
    OPEN_CFW_AEABI_BASE_PCS int64_t (*signed_convert)(double) = __aeabi_d2lz;
    OPEN_CFW_AEABI_BASE_PCS uint64_t (*unsigned_convert)(float) = __aeabi_f2ulz;

    (void)copy;
    (void)fill;
    (void)copy4;
    (void)signed_convert;
    (void)unsigned_convert;
}
