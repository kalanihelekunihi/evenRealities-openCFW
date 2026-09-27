/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-089 retained island.
 */

#if defined(OPEN_CFW_AM089_0X00513E4C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513e4c(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am089_0x00513e4c_0000:\n"
        "b L_open_cfw_runtime_am089_0x00513e4c_0000\n"
        "push {r4, lr}\n"
        "mov r4, r0\n"
        "mov r1, r4\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513E56_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513e56(void)
{
    __asm__ volatile(
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x490d\n"
        ".inst.n 0x7808\n"
        ".inst.n 0xb118\n"
        ".inst.n 0x4620\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x4010\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0xbd10\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513ED0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513ed0(void)
{
    __asm__ volatile(
        "movs r2, r0\n"
        "lsrs r0, r0, #0x20\n"
        "movs r1, r1\n"
        "strh r0, [r0]\n"
        "movs r0, r0\n"
        "movs r0, r0\n"
        "movs r0, r0\n"
        "movs r0, r0\n"
        "lsls r0, r0, #0x10\n"
        "movs r0, r0\n"
        "movs r0, r0\n"
        "movs r0, r0\n"
        "lsrs r0, r0, #0x20\n"
        "movs r0, r0\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513EEE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513eee(void)
{
    __asm__ volatile(
        ".inst.n 0x0000\n"
        ".inst.n 0x0001\n"
        ".inst.n 0xb209\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd4fe\n"
        ".inst.n 0x2201\n"
        ".inst.n 0xf010\n"
        ".inst.n 0x011f\n"
        ".inst.n 0x408a\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x1358\n"
        ".inst.n 0xb200\n"
        ".inst.n 0x0940\n"
        ".inst.n 0xf841\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513F0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513f0c(void)
{
    __asm__ volatile(
        ".inst.n 0x4770\n"
        ".inst.n 0x0001\n"
        ".inst.n 0xb209\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd409\n"
        ".inst.n 0x2201\n"
        ".inst.n 0xf010\n"
        ".inst.n 0x011f\n"
        ".inst.n 0x408a\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x1340\n"
        ".inst.n 0xb200\n"
        ".inst.n 0x0940\n"
        ".inst.n 0xf841\n"
        ".inst.n 0x2020\n"
        ".inst.n 0x4770\n"
        ".inst.n 0x0002\n"
        ".inst.n 0xb212\n"
        ".inst.n 0x2a00\n"
        ".inst.n 0xd4fe\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513F34_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513f34(void)
{
    __asm__ volatile(
        ".inst.n 0x0109\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x232c\n"
        ".inst.n 0xb200\n"
        ".inst.n 0x5411\n"
        ".inst.n 0xe008\n"
        ".inst.n 0x0109\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x2324\n"
        ".inst.n 0xb200\n"
        ".inst.n 0xf010\n"
        ".inst.n 0x000f\n"
        ".inst.n 0x4410\n"
        ".inst.n 0xf800\n"
        ".inst.n 0x1c04\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb538\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x70a4\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x20f8\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x201c\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0025\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x70a4\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x42ac\n"
        ".inst.n 0xd1f0\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x52ec\n"
        ".inst.n 0x602c\n"
        ".inst.n 0x4669\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x02e8\n"
        ".inst.n 0x6800\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513F92_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513f92(void)
{
    __asm__ volatile(
        "cmp r0, #0\n"
        "L_open_cfw_runtime_am089_0x00513f92_0002:\n"
        "beq L_open_cfw_runtime_am089_0x00513f92_0002\n"
        "movs.w r0, #0x10000000\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00513F9C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00513f9c(void)
{
    __asm__ volatile(
        ".inst.n 0x12d8\n"
        ".inst.n 0x6008\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x12d4\n"
        ".inst.n 0x6808\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd002\n"
        ".inst.n 0x6828\n"
        ".inst.n 0x6809\n"
        ".inst.n 0x4788\n"
        ".inst.n 0xbd31\n"
        ".inst.n 0xb580\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xbd01\n"
        ".inst.n 0xb51f\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x20f8\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2104\n"
        ".inst.n 0x201c\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x201c\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4298\n"
        ".inst.n 0x6820\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd105\n"
        ".inst.n 0x2203\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x6020\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4290\n"
        ".inst.n 0x68e0\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd1fe\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5298\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0020\n"
        ".inst.n 0x4669\n"
        ".inst.n 0x2210\n"
        ".inst.n 0xf7ff\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051400A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051400a(void)
{
    __asm__ volatile(
        ".inst.n 0x0020\n"
        ".inst.n 0x6880\n"
        ".inst.n 0x46c0\n"
        ".inst.n 0x2101\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd1fe\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0x4992\n"
        ".inst.n 0x6008\n"
        ".inst.n 0x2000\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514026_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514026(void)
{
    __asm__ volatile(
        ".inst.n 0xb004\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb580\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x717a\n"
        ".inst.n 0x488f\n"
        ".inst.n 0x6800\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2801\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051403C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051403c(void)
{
    __asm__ volatile(
        ".inst.n 0x4890\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xe7fe\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514046_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514046(void)
{
    __asm__ volatile(
        ".inst.n 0xb510\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0xf7ff\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514050_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514050(void)
{
    __asm__ volatile(
        ".inst.n 0x4886\n"
        ".inst.n 0x6800\n"
        ".inst.n 0x42a0\n"
        ".inst.n 0xdbfe\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0x4989\n"
        ".inst.n 0x6809\n"
        ".inst.n 0x1840\n"
        ".inst.n 0x6800\n"
        ".inst.n 0x4770\n"
        ".inst.n 0x4a87\n"
        ".inst.n 0x6812\n"
        ".inst.n 0x1880\n"
        ".inst.n 0x6001\n"
        ".inst.n 0x4770\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514070_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514070(void)
{
    __asm__ volatile(
        ".inst.n 0x2800\n"
        ".inst.n 0xd007\n"
        ".inst.n 0x2802\n"
        ".inst.n 0xd003\n"
        ".inst.n 0xd304\n"
        ".inst.n 0x2803\n"
        ".inst.n 0xd004\n"
        ".inst.n 0xe005\n"
        ".inst.n 0x4881\n"
        ".inst.n 0xe004\n"
        ".inst.n 0x4881\n"
        ".inst.n 0xe002\n"
        ".inst.n 0x4881\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x487f\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb57f\n"
        ".inst.n 0x0005\n"
        ".inst.n 0x000c\n"
        ".inst.n 0x0016\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xffe8\n"
        ".inst.n 0x7e01\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd007\n"
        ".inst.n 0x361f\n"
        ".inst.n 0xf036\n"
        ".inst.n 0x061f\n"
        ".inst.n 0x2220\n"
        ".inst.n 0x0031\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0x2c01\n"
        ".inst.n 0xd003\n"
        ".inst.n 0x2c02\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd1fe\n"
        ".inst.n 0x2208\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005140C6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005140c6(void)
{
    __asm__ volatile(
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xe002\n"
        ".inst.n 0x0031\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x9002\n"
        ".inst.n 0x9003\n"
        ".inst.n 0x9600\n"
        ".inst.n 0x9401\n"
        ".inst.n 0x0028\n"
        ".inst.n 0x4669\n"
        ".inst.n 0x2210\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xbd7f\n"
        ".inst.n 0xb510\n"
        ".inst.n 0x0004\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005140EA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005140ea(void)
{
    __asm__ volatile(
        ".inst.n 0x6860\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x68a1\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x60a0\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x60e0\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6020\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0x6060\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb51c\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x6860\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x7e00\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd0fe\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051411A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051411a(void)
{
    __asm__ volatile(
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xb2c0\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd006\n"
        ".inst.n 0x6820\n"
        ".inst.n 0x9001\n"
        ".inst.n 0x68e0\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf3bf\n"
        ".inst.n 0x8f4f\n"
        ".inst.n 0xbd13\n"
        ".inst.n 0xb51c\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x6860\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x7e00\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514148_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514148(void)
{
    __asm__ volatile(
        ".inst.n 0xd001\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xb2c0\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd007\n"
        ".inst.n 0x6820\n"
        ".inst.n 0x9001\n"
        ".inst.n 0x68e0\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xbd13\n"
        ".inst.n 0xb538\n"
        ".inst.n 0x000c\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051416C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051416c(void)
{
    __asm__ volatile(
        "movs r5, r2\n"
        "bl .\n"
        "ldr r1, [r0, #0x14]\n"
        "ldr r2, [r0, #0x14]\n"
        "ldr r0, [r0, #0x10]\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514178_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514178(void)
{
    __asm__ volatile(
        "adds r0, r0, r2\n"
        "cmp r4, r1\n"
        "L_open_cfw_runtime_am089_0x00514178_0004:\n"
        "blo L_open_cfw_runtime_am089_0x00514178_0004\n"
        "adds r4, r5, r4\n"
        "cmp r0, r4\n"
        "L_open_cfw_runtime_am089_0x00514178_000a:\n"
        "bhs L_open_cfw_runtime_am089_0x00514178_000a\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514184_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514184(void)
{
    __asm__ volatile(
        "movs r0, #0\n"
        "b L_open_cfw_runtime_am089_0x00514184_0006\n"
        "movs r0, #1\n"
        "L_open_cfw_runtime_am089_0x00514184_0006:\n"
        "pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051418E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051418e(void)
{
    __asm__ volatile(
        "movs r1, r0\n"
        "ldr r0, [pc, #0xfc]\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514194_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514194(void)
{
    __asm__ volatile(
        "strb fp, [r5, #-0x2]!\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X0051419A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x0051419a(void)
{
    __asm__ volatile(
        ".inst.n 0x0001\n"
        ".inst.n 0x483c\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xbd01\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0x4930\n"
        ".inst.n 0x6008\n"
        ".inst.n 0x4770\n"
        ".inst.n 0x482f\n"
        ".inst.n 0x6800\n"
        ".inst.n 0x4770\n"
        ".inst.n 0x4831\n"
        ".inst.n 0x6940\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb57c\n"
        ".inst.n 0x0005\n"
        ".inst.n 0x000e\n"
        ".inst.n 0x4669\n"
        ".inst.n 0x2014\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd1fe\n"
        ".inst.n 0xb2ed\n"
        ".inst.n 0x2d00\n"
        ".inst.n 0xd003\n"
        ".inst.n 0x2d02\n"
        ".inst.n 0xd02a\n"
        ".inst.n 0xd329\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0xf89d\n"
        ".inst.n 0x0000\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2400\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0x2014\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd1f8\n"
        ".inst.n 0xb2f6\n"
        ".inst.n 0x2e00\n"
        ".inst.n 0xd0f5\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xffd1\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2401\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0x4820\n"
        ".inst.n 0x6800\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd0e5\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd0dd\n"
        ".inst.n 0x2401\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0xf89d\n"
        ".inst.n 0x0000\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd1fe\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514278_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514278(void)
{
    __asm__ volatile(
        ".inst.n 0x4818\n"
        ".inst.n 0x2007\n"
        ".inst.n 0x3bf0\n"
        ".inst.n 0x2007\n"
        ".inst.n 0xbacc\n"
        ".inst.n 0x0074\n"
        ".inst.n 0xf2f4\n"
        ".inst.n 0x0078\n"
        ".inst.n 0x0370\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x0354\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x0338\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x4f04\n"
        ".inst.n 0x2007\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x43f0\n"
        ".inst.n 0xb097\n"
        ".inst.n 0x4604\n"
        ".inst.n 0x460a\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xa813\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xa813\n"
        ".inst.n 0xe890\n"
        ".inst.n 0x006c\n"
        ".inst.n 0x4669\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xe881\n"
        ".inst.n 0x006c\n"
        ".inst.n 0x6880\n"
        ".inst.n 0x46c0\n"
        ".inst.n 0x4669\n"
        ".inst.n 0xe891\n"
        ".inst.n 0x006c\n"
        ".inst.n 0x9900\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xe880\n"
        ".inst.n 0x006c\n"
        ".inst.n 0x1088\n"
        ".inst.n 0xeb01\n"
        ".inst.n 0x7150\n"
        ".inst.n 0x2210\n"
        ".inst.n 0x920a\n"
        ".inst.n 0x10c9\n"
        ".inst.n 0x0049\n"
        ".inst.n 0x9108\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x9109\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x31ff\n"
        ".inst.n 0x2200\n"
        ".inst.n 0x910b\n"
        ".inst.n 0x920c\n"
        ".inst.n 0x920d\n"
        ".inst.n 0x920e\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005142F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005142f0(void)
{
    __asm__ volatile(
        ".inst.n 0x9111\n"
        ".inst.n 0x9112\n"
        ".inst.n 0x920a\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xe8b0\n"
        ".inst.n 0x43ec\n"
        ".inst.n 0xe8a4\n"
        ".inst.n 0x43ec\n"
        ".inst.n 0xe8b0\n"
        ".inst.n 0x41ec\n"
        ".inst.n 0xe8a4\n"
        ".inst.n 0x41ec\n"
        ".inst.n 0xb017\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x83f0\n"
        ".inst.n 0x0000\n"
        ".inst.n 0xb570\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xd105\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x4070\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xbfbd\n"
        ".inst.n 0x6a60\n"
        ".inst.n 0xb120\n"
        ".inst.n 0x7e21\n"
        ".inst.n 0x068a\n"
        ".inst.n 0xd401\n"
        ".inst.n 0xea4f\n"
        ".inst.n 0x0400\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x0864\n"
        ".inst.n 0x6801\n"
        ".inst.n 0x6848\n"
        ".inst.n 0x42a0\n"
        ".inst.n 0xd004\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x06c1\n"
        ".inst.n 0xd51f\n"
        ".inst.n 0x6a24\n"
        ".inst.n 0xe02a\n"
        ".inst.n 0xb910\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xe7f6\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6903\n"
        ".inst.n 0x1c95\n"
        ".inst.n 0x42ab\n"
        ".inst.n 0xda06\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0220\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xe7ea\n"
        ".inst.n 0x6883\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x25a0\n"
        ".inst.n 0x2600\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x5022\n"
        ".inst.n 0x1d1b\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x6022\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0208\n"
        ".inst.n 0x6182\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514384_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514384(void)
{
    __asm__ volatile(
        ".inst.n 0x46c0\n"
        ".inst.n 0x46c0\n"
        ".inst.n 0x4620\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfeac\n"
        ".inst.n 0x6a60\n"
        ".inst.n 0x6a25\n"
        ".inst.n 0xb110\n"
        ".inst.n 0x4620\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfeff\n"
        ".inst.n 0x462c\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd1c7\n"
        ".inst.n 0xbd70\n"
        ".inst.n 0x0000\n"
        ".inst.n 0xb510\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xd105\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x4010\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xbf73\n"
        ".inst.n 0x6a60\n"
        ".inst.n 0xb100\n"
        ".inst.n 0x4604\n"
        ".inst.n 0x6a60\n"
        ".inst.n 0xb128\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x17d4\n"
        ".inst.n 0x6809\n"
        ".inst.n 0x684a\n"
        ".inst.n 0x4294\n"
        ".inst.n 0xd008\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6160\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005143D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005143d4(void)
{
    __asm__ volatile(
        ".inst.n 0x69a0\n"
        ".inst.n 0xf020\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x61a0\n"
        ".inst.n 0xe006\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xe7f4\n"
        ".inst.n 0xbf00\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xff58\n"
        ".inst.n 0x6a24\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd1e4\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb5f0\n"
        ".inst.n 0xb081\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x460d\n"
        ".inst.n 0xbf08\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xd02b\n"
        ".inst.n 0x7b20\n"
        ".inst.n 0xf010\n"
        ".inst.n 0x0f07\n"
        ".inst.n 0xd10c\n"
        ".inst.n 0x6a60\n"
        ".inst.n 0xb100\n"
        ".inst.n 0x4604\n"
        ".inst.n 0x2d02\n"
        ".inst.n 0xda0a\n"
        ".inst.n 0x2502\n"
        ".inst.n 0x6920\n"
        ".inst.n 0x0080\n"
        ".inst.n 0xfb90\n"
        ".inst.n 0xf1f5\n"
        ".inst.n 0xfb05\n"
        ".inst.n 0x0011\n"
        ".inst.n 0xb1f8\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x4080\n"
        ".inst.n 0xe017\n"
        ".inst.n 0xddf4\n"
        ".inst.n 0x6920\n"
        ".inst.n 0x0080\n"
        ".inst.n 0xfb90\n"
        ".inst.n 0xf1f5\n"
        ".inst.n 0xf5b1\n"
        ".inst.n 0x7f00\n"
        ".inst.n 0xdaed\n"
        ".inst.n 0x07ea\n"
        ".inst.n 0xbf48\n"
        ".inst.n 0x1c6d\n"
        ".inst.n 0x2d04\n"
        ".inst.n 0xdb05\n"
        ".inst.n 0x1ead\n"
        ".inst.n 0xfb90\n"
        ".inst.n 0xf1f5\n"
        ".inst.n 0xf5b1\n"
        ".inst.n 0x7f00\n"
        ".inst.n 0xdbf7\n"
        ".inst.n 0xf5b1\n"
        ".inst.n 0x7f00\n"
        ".inst.n 0xdadf\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x3080\n"
        ".inst.n 0xb001\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x40f0\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xbf1b\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x6730\n"
        ".inst.n 0x6831\n"
        ".inst.n 0x6848\n"
        ".inst.n 0xb1c0\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6903\n"
        ".inst.n 0x1c97\n"
        ".inst.n 0x42bb\n"
        ".inst.n 0xdb0d\n"
        ".inst.n 0x6883\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x27a0\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x0c00\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x7022\n"
        ".inst.n 0x1d1b\n"
        ".inst.n 0xf843\n"
        ".inst.n 0xc022\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0208\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0220\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xb924\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xfef8\n"
        ".inst.n 0xe003\n"
        ".inst.n 0x69a0\n"
        ".inst.n 0xf040\n"
        ".inst.n 0x0020\n"
        ".inst.n 0x61a0\n"
        ".inst.n 0xf04f\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005144BA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005144ba(void)
{
    __asm__ volatile(
        ".inst.n 0x6360\n"
        ".inst.n 0x63a0\n"
        ".inst.n 0x6920\n"
        ".inst.n 0xfb90\n"
        ".inst.n 0xf0f5\n"
        ".inst.n 0x07c1\n"
        ".inst.n 0xbf48\n"
        ".inst.n 0x1e40\n"
        ".inst.n 0x62e0\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x62a5\n"
        ".inst.n 0x6320\n"
        ".inst.n 0x6831\n"
        ".inst.n 0x604c\n"
        ".inst.n 0xb001\n"
        ".inst.n 0xbdf0\n"
        ".inst.n 0xb430\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x06b8\n"
        ".inst.n 0x6801\n"
        ".inst.n 0x6848\n"
        ".inst.n 0xb1a8\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6903\n"
        ".inst.n 0x1c94\n"
        ".inst.n 0x42a3\n"
        ".inst.n 0xdb0c\n"
        ".inst.n 0x6883\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x24a0\n"
        ".inst.n 0x2500\n"
        ".inst.n 0xf843\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005144FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005144fa(void)
{
    __asm__ volatile(
        "ands r2, r4\n"
        "adds r3, r3, #4\n"
        "str.w r5, [r3, r2, lsl #2]\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X00514504_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x00514504(void)
{
    __asm__ volatile(
        ".inst.n 0xf022\n"
        ".inst.n 0x0208\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0220\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xbc30\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x067c\n"
        ".inst.n 0x6801\n"
        ".inst.n 0x6848\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x47f0\n"
        ".inst.n 0x4606\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x566c\n"
        ".inst.n 0x6828\n"
        ".inst.n 0xb088\n"
        ".inst.n 0x6840\n"
        ".inst.n 0xb938\n"
        ".inst.n 0x2080\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xb008\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0x7e01\n"
        ".inst.n 0x078a\n"
        ".inst.n 0xd407\n"
        ".inst.n 0x2008\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xb008\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0x068b\n"
        ".inst.n 0xd508\n"
        ".inst.n 0x6ac2\n"
        ".inst.n 0x6943\n"
        ".inst.n 0x4611\n"
        ".inst.n 0x1ad2\n"
        ".inst.n 0xfb93\n"
        ".inst.n 0xf3f1\n"
        ".inst.n 0xfb01\n"
        ".inst.n 0x2203\n"
        ".inst.n 0xe002\n"
        ".inst.n 0x6902\n"
        ".inst.n 0x6941\n"
        ".inst.n 0x1a52\n"
        ".inst.n 0xeb02\n"
        ".inst.n 0x72d2\n"
        ".inst.n 0x1052\n"
        ".inst.n 0x1e92\n"
        ".inst.n 0x2a00\n"
        ".inst.n 0xdd40\n"
        ".inst.n 0x9200\n"
        ".inst.n 0xf002\n"
        ".inst.n 0x0e03\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x3180\n"
        ".inst.n 0x2400\n"
        ".inst.n 0xf04e\n"
        ".inst.n 0xc00d\n"
        ".inst.n 0x6943\n"
        ".inst.n 0x6882\n"
        ".inst.n 0xf842\n"
        ".inst.n 0x1023\n"
        ".inst.n 0x6882\n"
        ".inst.n 0x1c5b\n"
        ".inst.n 0xf842\n"
        ".inst.n 0x4023\n"
        ".inst.n 0x1c5b\n"
        ".inst.n 0x6143\n"
        ".inst.n 0xf00f\n"
        ".inst.n 0xc00d\n"
        ".inst.n 0xf8dd\n"
        ".inst.n 0xe000\n"
        ".inst.n 0xea4f\n"
        ".inst.n 0x0e9e\n"
        ".inst.n 0xf04e\n"
        ".inst.n 0xc827\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6883\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x1022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x4022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x1022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x4022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x1022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x4022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x1022\n"
        ".inst.n 0x6883\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x4022\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0xf00f\n"
        ".inst.n 0xc827\n"
        ".inst.n 0x6a04\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd17c\n"
        ".inst.n 0x203c\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xd107\n"
        ".inst.n 0x2010\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xb008\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0x1cb2\n"
        ".inst.n 0x00d2\n"
        ".inst.n 0xf5b2\n"
        ".inst.n 0x6f80\n"
        ".inst.n 0xdd22\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xa904\n"
        ".inst.n 0xe891\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xe880\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0x6880\n"
        ".inst.n 0x46c0\n"
        ".inst.n 0x4669\n"
        ".inst.n 0xe891\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0xf10d\n"
        ".inst.n 0x0c10\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xe880\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0xe89c\n"
        ".inst.n 0x4700\n"
        ".inst.n 0x9800\n"
        ".inst.n 0x1081\n"
        ".inst.n 0xeb00\n"
        ".inst.n 0x7051\n"
        ".inst.n 0xe884\n"
        ".inst.n 0x4700\n"
        ".inst.n 0x10c0\n"
        ".inst.n 0x0040\n"
        ".inst.n 0x6120\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6160\n"
        ".inst.n 0x61a0\n"
        ".inst.n 0xe024\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x6280\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xa904\n"
        ".inst.n 0xe891\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0x4668\n"
        ".inst.n 0xe880\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0x6880\n"
        ".inst.n 0x46c0\n"
        ".inst.n 0x4669\n"
        ".inst.n 0xe891\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0xf10d\n"
        ".inst.n 0x0c10\n"
        ".inst.n 0xa804\n"
        ".inst.n 0xe880\n"
        ".inst.n 0x00cc\n"
        ".inst.n 0xe89c\n"
        ".inst.n 0x4700\n"
        ".inst.n 0x9800\n"
        ".inst.n 0x1081\n"
        ".inst.n 0xeb00\n"
        ".inst.n 0x7051\n"
        ".inst.n 0xe884\n"
        ".inst.n 0x4700\n"
        ".inst.n 0x2102\n"
        ".inst.n 0x10c0\n"
        ".inst.n 0x0040\n"
        ".inst.n 0x6120\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6160\n"
        ".inst.n 0x61a1\n"
        ".inst.n 0x6260\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0x61e0\n"
        ".inst.n 0x6360\n"
        ".inst.n 0x63a0\n"
        ".inst.n 0x68a0\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x62a1\n"
        ".inst.n 0x62e1\n"
        ".inst.n 0x6321\n"
        ".inst.n 0x6221\n"
        ".inst.n 0xb950\n"
        ".inst.n 0x2010\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0x4620\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xf04f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xb008\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0x6829\n"
        ".inst.n 0x684a\n"
        ".inst.n 0x6a50\n"
        ".inst.n 0xb100\n"
        ".inst.n 0x4602\n"
        ".inst.n 0x6262\n"
        ".inst.n 0x6848\n"
        ".inst.n 0x6981\n"
        ".inst.n 0xf021\n"
        ".inst.n 0x010c\n"
        ".inst.n 0x61a1\n"
        ".inst.n 0x6828\n"
        ".inst.n 0x6840\n"
        ".inst.n 0xb920\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xe003\n"
        ".inst.n 0x6981\n"
        ".inst.n 0xf041\n"
        ".inst.n 0x0104\n"
        ".inst.n 0x6181\n"
        ".inst.n 0x6829\n"
        ".inst.n 0x23f0\n"
        ".inst.n 0x6848\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6885\n"
        ".inst.n 0xf845\n"
        ".inst.n 0x3022\n"
        ".inst.n 0x68e3\n"
        ".inst.n 0x6885\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf845\n"
        ".inst.n 0x3022\n"
        ".inst.n 0x6885\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0x23f4\n"
        ".inst.n 0xf845\n"
        ".inst.n 0x3022\n"
        ".inst.n 0x6923\n"
        ".inst.n 0x6885\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf845\n"
        ".inst.n 0x3022\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x6142\n"
        ".inst.n 0x6204\n"
        ".inst.n 0xb914\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xe005\n"
        ".inst.n 0x7b20\n"
        ".inst.n 0xf010\n"
        ".inst.n 0x0f07\n"
        ".inst.n 0xd004\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x4080\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfffe\n"
        ".inst.n 0xe7fe\n"
        ".inst.n 0x6848\n"
        ".inst.n 0xb1b8\n"
        ".inst.n 0x6942\n"
        ".inst.n 0x6903\n"
        ".inst.n 0x1c95\n"
        ".inst.n 0x42ab\n"
        ".inst.n 0xdb0c\n"
        ".inst.n 0x6883\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x25a0\n"
        ".inst.n 0x2600\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x5022\n"
        ".inst.n 0x1d1b\n"
        ".inst.n 0xf843\n"
        ".inst.n 0x6022\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0208\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x6982\n"
        ".inst.n 0xf022\n"
        ".inst.n 0x0220\n"
        ".inst.n 0x6182\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x6048\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x0742\n"
        ".inst.n 0xd5fe\n"
        ".inst.n 0x6a24\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x0742\n"
        ".inst.n 0xd5fe\n"
        ".inst.n 0x6a24\n"
    );
}
#endif

#if defined(OPEN_CFW_AM089_0X005147B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am089_0x005147b0(void)
{
    __asm__ volatile(
        ".inst.n 0x7e20\n"
        ".inst.n 0x0742\n"
        ".inst.n 0xd507\n"
        ".inst.n 0x6a24\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x0742\n"
        ".inst.n 0xd503\n"
        ".inst.n 0x6a24\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x0742\n"
        ".inst.n 0xd4ef\n"
        ".inst.n 0x604c\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xb008\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0xb510\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xd105\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x5000\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x4010\n"
        ".inst.n 0xf79c\n"
        ".inst.n 0xbd5d\n"
        ".inst.n 0x7e21\n"
        ".inst.n 0x6960\n"
        ".inst.n 0x068a\n"
        ".inst.n 0xd506\n"
        ".inst.n 0x6ae1\n"
        ".inst.n 0xfb90\n"
        ".inst.n 0xf3f1\n"
        ".inst.n 0xfb01\n"
        ".inst.n 0x0013\n"
        ".inst.n 0xb908\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb3a0\n"
        ".inst.n 0x4620\n"
        ".inst.n 0xf000\n"
        ".inst.n 0xf9ce\n"
        ".inst.n 0x7e20\n"
        ".inst.n 0x0681\n"
        ".inst.n 0xd51f\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x0390\n"
        ".inst.n 0x6802\n"
        ".inst.n 0xf892\n"
        ".inst.n 0x10f9\n"
        ".inst.n 0x2901\n"
        ".inst.n 0xbf1f\n"
        ".inst.n 0x6aa1\n"
        ".inst.n 0x088a\n"
        ".inst.n 0x6b20\n"
        ".inst.n 0x4290\n"
        ".inst.n 0xd00d\n"
        ".inst.n 0xebb0\n"
        ".inst.n 0x0f51\n"
        ".inst.n 0xbf1c\n"
        ".inst.n 0xeb02\n"
        ".inst.n 0x0242\n"
        ".inst.n 0x4290\n"
        ".inst.n 0xd006\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xbf1e\n"
        ".inst.n 0x6b60\n"
        ".inst.n 0xf06f\n"
        ".inst.n 0x417f\n"
        ".inst.n 0x4288\n"
        ".inst.n 0xd108\n"
        ".inst.n 0x6b60\n"
        ".inst.n 0xf00f\n"
        ".inst.n 0xfb78\n"
        ".inst.n 0x6b60\n"
        ".inst.n 0x61e0\n"
    );
}
#endif
