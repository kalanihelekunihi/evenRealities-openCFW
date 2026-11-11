#ifndef R1_NATIVE_GOMORE_RECORD8_H
#define R1_NATIVE_GOMORE_RECORD8_H
#include <stdint.h>
uint32_t r1_gomore_record8_get_native(uint32_t,volatile void *);
uint32_t r1_gomore_record8_apply_native(const volatile void *);
uintptr_t r1_gomore_record8_select_native(volatile void *,const volatile void *,uint32_t);
uint32_t r1_gomore_record8_valid_native(const volatile void *,const volatile void *);
uint32_t r1_gomore_record8_commit_native(volatile void *,const volatile void *);
#endif
