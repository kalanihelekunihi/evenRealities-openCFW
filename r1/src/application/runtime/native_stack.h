#ifndef R1_NATIVE_STACK_H
#define R1_NATIVE_STACK_H
#include <stdint.h>

/* Observe the caller's compiled SP without allocating a frame. This does not
 * establish the caller's frame layout: offsets require independent native
 * ABI validation for each compiler/profile. Never retain this pointer across
 * calls when a fresh observation is required. */
__attribute__((always_inline)) static inline volatile uint32_t *r1_native_stack_words(void)
{
#if defined(__clang__)
    register volatile uint32_t *frame __asm__("sp");
    __asm__ volatile("" : "=r"(frame) : : "memory");
    return frame;
#else
    /* A reserved-SP output can become an assignment under GCC. Its builtin
     * reads SP without emitting a move into the stack-pointer register. */
    return __builtin_stack_save();
#endif
}
#endif
