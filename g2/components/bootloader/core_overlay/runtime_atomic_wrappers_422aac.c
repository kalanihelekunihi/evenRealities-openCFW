/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of three G2 bootloader low-level runtime leaves. */

typedef __UINT32_TYPE__ open_cfw_atomic_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_ATOMIC_ATTR __attribute__((used, naked, noinline))
extern open_cfw_atomic_u32 open_cfw_bootloader_retained_query_41cdb8(void);

OPEN_CFW_ATOMIC_ATTR void open_cfw_bootloader_atomic_snapshot3_422aac(void)
{
    __asm__ volatile(
        "push {r1, r4}\n"
        "mrs r4, primask\n"
        "cpsid i\n"
        "ldr r1, [r0]\n"
        "ldr r2, [r0]\n"
        "ldr r3, [r0]\n"
        "msr primask, r4\n"
        "pop {r0, r4}\n"
        "str r1, [r0]\n"
        "str r2, [r0, #4]\n"
        "str r3, [r0, #8]\n"
        "bx lr\n");
}

OPEN_CFW_ATOMIC_ATTR void open_cfw_bootloader_noop_422ac8(void)
{
    __asm__ volatile("bx lr\n");
}

OPEN_CFW_ATOMIC_ATTR void open_cfw_bootloader_retained_query_wrapper_422aca(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl open_cfw_bootloader_retained_query_41cdb8\n"
        "pop {r0, pc}\n");
}
#else
extern open_cfw_atomic_u32 open_cfw_atomic_host_retained_query(void);
void open_cfw_bootloader_atomic_snapshot3_422aac(
    const volatile open_cfw_atomic_u32 *source,
    open_cfw_atomic_u32 destination[3])
{
    open_cfw_atomic_u32 a=*source,b=*source,c=*source;
    destination[0]=a; destination[1]=b; destination[2]=c;
}
void open_cfw_bootloader_noop_422ac8(void) {}
open_cfw_atomic_u32 open_cfw_bootloader_retained_query_wrapper_422aca(void)
{
    return open_cfw_atomic_host_retained_query();
}
#endif
