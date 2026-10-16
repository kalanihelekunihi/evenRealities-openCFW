#include <stdint.h>
/* Native ordering uses encoded integer keys, without IEEE NaN handling.
 * The EABI entries return transformed keys in R0..R3 and comparison APSR flags.
 * C computes the keys; final source-compilable comparisons preserve exact
 * 32-bit subtraction NZCV semantics, including overflow and the incoming Q. */
static inline uint64_t key(uint64_t bits)
{ return bits>>63 ? bits : UINT64_C(0x8000000000000000)-bits; }
__attribute__((noinline,used))
static uint32_t reverse_worker(uint64_t a,uint64_t b)
{
    a=key(a);b=key(b);
    register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32);
    register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);
    __asm__ volatile("cmp %3,%1\n\tit eq\n\tcmpeq %2,%0" : "+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3) : : "cc");
    return r0;
}
__attribute__((noinline,used))
static uint32_t forward_worker(uint64_t a,uint64_t b)
{
    a=key(a);b=key(b);
    register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32);
    register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);
    __asm__ volatile("cmp %1,%3\n\tit eq\n\tcmpeq %0,%2" : "+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3) : : "cc");
    return r0;
}

/* Native leaf helpers preserve R12, which optimized C uses as scratch.
 * These ABI adapters preserve it without guessing an incoming C register value.
 * Source private frames differ from native and remain an explicit gate. */
__attribute__((naked))
uint32_t r1_binary64_compare_reverse_flags(uint64_t a __attribute__((unused)),uint64_t b __attribute__((unused)))
{
    __asm__ volatile("push.w {r12,lr}\n\tbl reverse_worker\n\tpop.w {r12,lr}\n\tbx lr");
}
__attribute__((naked))
uint32_t r1_binary64_compare_flags(uint64_t a __attribute__((unused)),uint64_t b __attribute__((unused)))
{
    __asm__ volatile("push.w {r12,lr}\n\tbl forward_worker\n\tpop.w {r12,lr}\n\tbx lr");
}
