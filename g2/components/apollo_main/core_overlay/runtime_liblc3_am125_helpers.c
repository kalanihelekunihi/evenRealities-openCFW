/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-125 retained island.
 */

#if defined(OPEN_CFW_AM125_0X0055EFF0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055eff0(void)
{
    __asm__ volatile(
        "str r0, [sp, #4]\n"
        "movs r0, #0xfb\n"
        "str r0, [sp]\n"
        "ldr r3, [pc, #0xc8]\n"
        "ldr r2, [pc, #0x48]\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F07A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f07a(void)
{
    __asm__ volatile(
        ".inst.n 0x0076\n"
        ".inst.n 0xe624\n"
        ".inst.n 0x006f\n"
        ".inst.n 0xa66c\n"
        ".inst.n 0x006e\n"
        ".inst.n 0xec5c\n"
        ".inst.n 0x0078\n"
        ".inst.n 0x0101\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x4590\n"
        ".inst.n 0x0078\n"
        ".inst.n 0xbfac\n"
        ".inst.n 0x0075\n"
        ".inst.n 0xbf88\n"
        ".inst.n 0x0075\n"
        ".inst.n 0xf8ac\n"
        ".inst.n 0x0072\n"
        ".inst.n 0xec64\n"
        ".inst.n 0x0078\n"
        ".inst.n 0x0102\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xa5c0\n"
        ".inst.n 0x0071\n"
        ".inst.n 0xe66c\n"
        ".inst.n 0x006f\n"
        ".inst.n 0xec6c\n"
        ".inst.n 0x0078\n"
        ".inst.n 0x6f70\n"
        ".inst.n 0x0076\n"
        ".inst.n 0xd00c\n"
        ".inst.n 0x0077\n"
        ".inst.n 0xa394\n"
        ".inst.n 0x0073\n"
        ".inst.n 0x4e30\n"
        ".inst.n 0x0072\n"
        ".inst.n 0x3b6c\n"
        ".inst.n 0x0077\n"
        ".inst.n 0xe6b4\n"
        ".inst.n 0x006f\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5202\n"
        ".inst.n 0x5a80\n"
        ".inst.n 0xb289\n"
        ".inst.n 0x1808\n"
        ".inst.n 0x2140\n"
        ".inst.n 0xfb90\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F0D8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f0d8(void)
{
    __asm__ volatile(
        ".inst.n 0xfb01\n"
        ".inst.n 0x0012\n"
        ".inst.n 0xb280\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb570\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4b1c\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x0b3c\n"
        ".inst.n 0x6801\n"
        ".inst.n 0x1c49\n"
        ".inst.n 0x6001\n"
        ".inst.n 0x6805\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x510c\n"
        ".inst.n 0x2200\n"
        ".inst.n 0x0026\n"
        ".inst.n 0x0030\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xf802\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5004\n"
        ".inst.n 0x5025\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5108\n"
        ".inst.n 0x5060\n"
        ".inst.n 0xbd70\n"
        ".inst.n 0xb510\n"
        ".inst.n 0xf24a\n"
        ".inst.n 0x11dc\n"
        ".inst.n 0x2200\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4b0c\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf6a4\n"
        ".inst.n 0xfff1\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xffdd\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb580\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xffd9\n"
        ".inst.n 0xbd01\n"
        ".inst.n 0xb510\n"
        ".inst.n 0xf640\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F134_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f134(void)
{
    __asm__ volatile(
        ".inst.n 0x0106\n"
        ".inst.n 0x2200\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4aec\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf6a4\n"
        ".inst.n 0xffe1\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb510\n"
        ".inst.n 0xf640\n"
        ".inst.n 0x014c\n"
        ".inst.n 0x2200\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4adc\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf6a4\n"
        ".inst.n 0xffd7\n"
        ".inst.n 0xbd10\n"
        ".inst.n 0xb470\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd008\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd006\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x4ac4\n"
        ".inst.n 0xf24a\n"
        ".inst.n 0x12d9\n"
        ".inst.n 0x5ca2\n"
        ".inst.n 0x2a00\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe017\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5268\n"
        ".inst.n 0x58a3\n"
        ".inst.n 0x2b0b\n"
        ".inst.n 0xd300\n"
        ".inst.n 0x230a\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F180_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f180(void)
{
    __asm__ volatile(
        ".inst.n 0x2200\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0x429a\n"
        ".inst.n 0xd20b\n"
        ".inst.n 0x2590\n"
        ".inst.n 0xfb05\n"
        ".inst.n 0xf502\n"
        ".inst.n 0x4425\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x56fc\n"
        ".inst.n 0x59ad\n"
        ".inst.n 0x4285\n"
        ".inst.n 0xd1f3\n"
        ".inst.n 0x600a\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xbc70\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb580\n"
        ".inst.n 0xf110\n"
        ".inst.n 0x0f01\n"
        ".inst.n 0xd10b\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x506c\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x1a70\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F218_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f218(void)
{
    __asm__ volatile(
        ".inst.n 0xf8df\n"
        ".inst.n 0x4a0c\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x506c\n"
        ".inst.n 0xeb04\n"
        ".inst.n 0x0500\n"
        ".inst.n 0x2190\n"
        ".inst.n 0x2200\n"
        ".inst.n 0x002e\n"
        ".inst.n 0x0030\n"
        ".inst.n 0xf6a4\n"
        ".inst.n 0xff6a\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0x6028\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xf885\n"
        ".inst.n 0x1086\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5164\n"
        ".inst.n 0x5060\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xf24a\n"
        ".inst.n 0x11da\n"
        ".inst.n 0x5460\n"
        ".inst.n 0xbd70\n"
        ".inst.n 0xb570\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe017\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F294_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f294(void)
{
    __asm__ volatile(
        ".inst.n 0x000d\n"
        ".inst.n 0x0016\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd008\n"
        ".inst.n 0x2e00\n"
        ".inst.n 0xd006\n"
        ".inst.n 0x2d00\n"
        ".inst.n 0xd004\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x4105\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F2B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f2b0(void)
{
    __asm__ volatile(
        ".inst.n 0xe01b\n"
        ".inst.n 0x5a67\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x1e7f\n"
        ".inst.n 0x0038\n"
        ".inst.n 0xb280\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd013\n"
        ".inst.n 0xf1b7\n"
        ".inst.n 0x0801\n"
        ".inst.n 0x4641\n"
        ".inst.n 0xb289\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfefd\n"
        ".inst.n 0xb280\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F2D0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f2d0(void)
{
    __asm__ volatile(
        ".inst.n 0xf44f\n"
        ".inst.n 0x7105\n"
        ".inst.n 0x4348\n"
        ".inst.n 0x4420\n"
        ".inst.n 0xf8d0\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F2DA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f2da(void)
{
    __asm__ volatile(
        ".inst.n 0x0208\n"
        ".inst.n 0x42a8\n"
        ".inst.n 0xd1ea\n"
        ".inst.n 0xf8a6\n"
        ".inst.n 0x8000\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F2EA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f2ea(void)
{
    __asm__ volatile(
        ".inst.n 0xe8bd\n"
        ".inst.n 0x81f0\n"
        ".inst.n 0xb538\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x0015\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F2F4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f2f4(void)
{
    __asm__ volatile(
        ".inst.n 0x2c00\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2900\n"
        ".inst.n 0xd100\n"
        ".inst.n 0xe01b\n"
        ".inst.n 0x7808\n"
        ".inst.n 0x7020\n"
        ".inst.n 0x7808\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F304_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f304(void)
{
    __asm__ volatile(
        ".inst.n 0x2802\n"
        ".inst.n 0xd004\n"
        ".inst.n 0xd309\n"
        ".inst.n 0x2804\n"
        ".inst.n 0xd001\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F30E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f30e(void)
{
    __asm__ volatile(
        ".inst.n 0xd303\n"
        ".inst.n 0xe005\n"
        ".inst.n 0x2001\n"
        ".inst.n 0x7060\n"
        ".inst.n 0xe004\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F32A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f32a(void)
{
    __asm__ volatile(
        ".inst.n 0xf7ff\n"
        ".inst.n 0xff8f\n"
        ".inst.n 0xf8a4\n"
        ".inst.n 0x0204\n"
        ".inst.n 0xf8c4\n"
        ".inst.n 0x5208\n"
        ".inst.n 0xbd31\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x08ec\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x08ec\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x08b8\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x18dc\n"
        ".inst.n 0xf24a\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F4B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f4b8(void)
{
    __asm__ volatile(
        ".inst.n 0x42a2\n"
        ".inst.n 0xd219\n"
        ".inst.n 0x2590\n"
        ".inst.n 0xfb05\n"
        ".inst.n 0xf602\n"
        ".inst.n 0x441e\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x57fc\n"
        ".inst.n 0x59f6\n"
        ".inst.n 0x4286\n"
        ".inst.n 0xd1f3\n"
        ".inst.n 0xfb05\n"
        ".inst.n 0xf002\n"
        ".inst.n 0x4418\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x6482\n"
        ".inst.n 0x5501\n"
        ".inst.n 0xb2c9\n"
        ".inst.n 0x2902\n"
        ".inst.n 0xd006\n"
        ".inst.n 0x2000\n"
        ".inst.n 0x436a\n"
        ".inst.n 0xeb03\n"
        ".inst.n 0x0102\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x6288\n"
        ".inst.n 0x5488\n"
        ".inst.n 0xe7ff\n"
        ".inst.n 0xbcf0\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F4F2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f4f2(void)
{
    __asm__ volatile(
        ".inst.n 0x4770\n"
        ".inst.n 0xb51f\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xa903\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf7ff\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F544_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f544(void)
{
    __asm__ volatile(
        ".inst.n 0xfdd4\n"
        ".inst.n 0x07c0\n"
        ".inst.n 0xd403\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfdd0\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F54E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f54e(void)
{
    __asm__ volatile(
        ".inst.n 0x0740\n"
        ".inst.n 0xd507\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x16fc\n"
        ".inst.n 0x0023\n"
        ".inst.n 0x000a\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x6044\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfcae\n"
        ".inst.n 0xbd1f\n"
        ".inst.n 0xb580\n"
        ".inst.n 0x4669\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfdf6\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd00d\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x16b4\n"
        ".inst.n 0x9a00\n"
        ".inst.n 0x2090\n"
        ".inst.n 0x4342\n"
        ".inst.n 0xeb01\n"
        ".inst.n 0x0002\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x6188\n"
        ".inst.n 0x5c40\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2001\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F5FE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f5fe(void)
{
    __asm__ volatile(
        ".inst.n 0xd507\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x165c\n"
        ".inst.n 0x002b\n"
        ".inst.n 0x000a\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x6004\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfc57\n"
        ".inst.n 0xe02d\n"
        ".inst.n 0xf6b2\n"
        ".inst.n 0xfdfa\n"
        ".inst.n 0xf8c4\n"
        ".inst.n 0x0088\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfd68\n"
        ".inst.n 0x0780\n"
        ".inst.n 0xd512\n"
        ".inst.n 0xf8d4\n"
        ".inst.n 0x0088\n"
        ".inst.n 0x9003\n"
        ".inst.n 0x9502\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x0638\n"
        ".inst.n 0x9001\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x70b2\n"
        ".inst.n 0x9000\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x3624\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x260c\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x160c\n"
        ".inst.n 0x2003\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xffa6\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfd51\n"
        ".inst.n 0x07c0\n"
        ".inst.n 0xd403\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfd4d\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F654_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f654(void)
{
    __asm__ volatile(
        ".inst.n 0x0740\n"
        ".inst.n 0xd50a\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x260c\n"
        ".inst.n 0xf8d4\n"
        ".inst.n 0x0088\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x002b\n"
        ".inst.n 0x0011\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x6048\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfc28\n"
        ".inst.n 0xb005\n"
        ".inst.n 0xbd30\n"
        ".inst.n 0xb580\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfd98\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd002\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xf8c0\n"
        ".inst.n 0x1088\n"
        ".inst.n 0xbd01\n"
        ".inst.n 0xb430\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x25a0\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5068\n"
        ".inst.n 0x5811\n"
        ".inst.n 0x290b\n"
        ".inst.n 0xd300\n"
        ".inst.n 0x210a\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe008\n"
        ".inst.n 0x2300\n"
        ".inst.n 0x2490\n"
        ".inst.n 0xfb04\n"
        ".inst.n 0xf400\n"
        ".inst.n 0x4414\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x6584\n"
        ".inst.n 0x5163\n"
        ".inst.n 0x1c40\n"
        ".inst.n 0x4288\n"
        ".inst.n 0xd3f4\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x51f4\n"
        ".inst.n 0x5050\n"
        ".inst.n 0xbc30\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xb538\n"
        ".inst.n 0x000d\n"
        ".inst.n 0x2d00\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe016\n"
        ".inst.n 0x2100\n"
        ".inst.n 0x6029\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfd6c\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe00e\n"
        ".inst.n 0xf8d0\n"
        ".inst.n 0x4088\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe008\n"
        ".inst.n 0xf6b2\n"
        ".inst.n 0xfd91\n"
        ".inst.n 0x42a0\n"
        ".inst.n 0xd201\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe002\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F6F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f6f0(void)
{
    __asm__ volatile(
        ".inst.n 0x1b04\n"
        ".inst.n 0x602c\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xbd32\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x41f0\n"
        ".inst.n 0x0004\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd102\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xe070\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x651c\n"
        ".inst.n 0xf240\n"
        ".inst.n 0x71ff\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x7800\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x0802\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F74C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f74c(void)
{
    __asm__ volatile(
        ".inst.n 0x2800\n"
        ".inst.n 0xd003\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x0802\n"
        ".inst.n 0xf8a6\n"
        ".inst.n 0x0800\n"
        ".inst.n 0xf894\n"
        ".inst.n 0x0202\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf886\n"
        ".inst.n 0x0804\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xf886\n"
        ".inst.n 0x0805\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe03a\n"
        ".inst.n 0x8825\n"
        ".inst.n 0x1bc8\n"
        ".inst.n 0x42a8\n"
        ".inst.n 0xd201\n"
        ".inst.n 0x000d\n"
        ".inst.n 0x1bed\n"
        ".inst.n 0x2d00\n"
        ".inst.n 0xd006\n"
        ".inst.n 0x002a\n"
        ".inst.n 0x1ca1\n"
        ".inst.n 0xeb06\n"
        ".inst.n 0x0807\n"
        ".inst.n 0x4640\n"
        ".inst.n 0xf6a2\n"
        ".inst.n 0xfa39\n"
        ".inst.n 0x19ef\n"
        ".inst.n 0xf8a6\n"
        ".inst.n 0x7802\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x1802\n"
        ".inst.n 0x5470\n"
        ".inst.n 0xf894\n"
        ".inst.n 0x0202\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd003\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x0802\n"
        ".inst.n 0xf8a6\n"
        ".inst.n 0x0800\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x0802\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x1800\n"
        ".inst.n 0x4288\n"
        ".inst.n 0xd203\n"
        ".inst.n 0xf8b6\n"
        ".inst.n 0x0802\n"
        ".inst.n 0xf8a6\n"
        ".inst.n 0x0800\n"
        ".inst.n 0xf894\n"
        ".inst.n 0x0202\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf886\n"
        ".inst.n 0x0804\n"
        ".inst.n 0xf894\n"
        ".inst.n 0x0203\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd001\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf886\n"
        ".inst.n 0x0805\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x81f0\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x4ff8\n"
        ".inst.n 0x0005\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x6430\n"
        ".inst.n 0xf649\n"
        ".inst.n 0x309c\n"
        ".inst.n 0x4430\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x2d00\n"
        ".inst.n 0xd102\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x30ff\n"
        ".inst.n 0xe07f\n"
        ".inst.n 0xf240\n"
        ".inst.n 0x623c\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5460\n"
        ".inst.n 0xeb06\n"
        ".inst.n 0x0104\n"
        ".inst.n 0x9f00\n"
        ".inst.n 0x0038\n"
        ".inst.n 0xf6a2\n"
        ".inst.n 0xf9f3\n"
        ".inst.n 0x9800\n"
        ".inst.n 0x6887\n"
        ".inst.n 0x2f0b\n"
        ".inst.n 0xd300\n"
        ".inst.n 0x270a\n"
        ".inst.n 0x6828\n"
        ".inst.n 0x5130\n"
        ".inst.n 0x6868\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5164\n"
        ".inst.n 0x5070\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5868\n"
        ".inst.n 0x8928\n"
        ".inst.n 0xf846\n"
        ".inst.n 0x0008\n"
        ".inst.n 0xf856\n"
        ".inst.n 0x0008\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F848_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f848(void)
{
    __asm__ volatile(
        ".inst.n 0xf846\n"
        ".inst.n 0x0008\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xf24a\n"
        ".inst.n 0x11d9\n"
        ".inst.n 0x5470\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x0900\n"
        ".inst.n 0xe00b\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf88a\n"
        ".inst.n 0x008c\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf8ca\n"
        ".inst.n 0x0088\n"
        ".inst.n 0xe002\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf88a\n"
        ".inst.n 0x008c\n"
        ".inst.n 0xf119\n"
        ".inst.n 0x0901\n"
        ".inst.n 0xf856\n"
        ".inst.n 0x0008\n"
        ".inst.n 0x4581\n"
        ".inst.n 0xd246\n"
        ".inst.n 0x2090\n"
        ".inst.n 0xfb00\n"
        ".inst.n 0xf109\n"
        ".inst.n 0x4431\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x52fc\n"
        ".inst.n 0xeb01\n"
        ".inst.n 0x0a02\n"
        ".inst.n 0x2400\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x1c49\n"
        ".inst.n 0x42b9\n"
        ".inst.n 0xd212\n"
        ".inst.n 0x9a00\n"
        ".inst.n 0xfb00\n"
        ".inst.n 0xf301\n"
        ".inst.n 0x441a\n"
        ".inst.n 0xf8d2\n"
        ".inst.n 0x209c\n"
        ".inst.n 0x2388\n"
        ".inst.n 0xfb03\n"
        ".inst.n 0xf309\n"
        ".inst.n 0x442b\n"
        ".inst.n 0x68db\n"
        ".inst.n 0x429a\n"
        ".inst.n 0xd1ef\n"
        ".inst.n 0x9a00\n"
        ".inst.n 0xfb00\n"
        ".inst.n 0xf001\n"
        ".inst.n 0x4410\n"
        ".inst.n 0xf110\n"
        ".inst.n 0x049c\n"
        ".inst.n 0x2288\n"
        ".inst.n 0x2088\n"
        ".inst.n 0xfb00\n"
        ".inst.n 0xf009\n"
        ".inst.n 0x4428\n"
        ".inst.n 0xf110\n"
        ".inst.n 0x010c\n"
        ".inst.n 0x46d3\n"
        ".inst.n 0x4658\n"
        ".inst.n 0xf6a2\n"
        ".inst.n 0xf999\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd0c1\n"
        ".inst.n 0xf89a\n"
        ".inst.n 0x0086\n"
        ".inst.n 0x2801\n"
        ".inst.n 0xd003\n"
        ".inst.n 0xf89a\n"
        ".inst.n 0x0086\n"
        ".inst.n 0x2802\n"
        ".inst.n 0xd104\n"
        ".inst.n 0xf8d4\n"
        ".inst.n 0x0088\n"
        ".inst.n 0xf8ca\n"
        ".inst.n 0x0088\n"
        ".inst.n 0xe002\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xf8ca\n"
        ".inst.n 0x0088\n"
        ".inst.n 0xf89a\n"
        ".inst.n 0x0086\n"
        ".inst.n 0x2802\n"
        ".inst.n 0xd1b4\n"
        ".inst.n 0xf894\n"
        ".inst.n 0x008c\n"
        ".inst.n 0xf88a\n"
        ".inst.n 0x008c\n"
        ".inst.n 0xe7b2\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x8ff2\n"
        ".inst.n 0xb53e\n"
        ".inst.n 0x0004\n"
        ".inst.n 0xf8df\n"
        ".inst.n 0x5314\n"
        ".inst.n 0xf24a\n"
        ".inst.n 0x10da\n"
        ".inst.n 0x5c28\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd00a\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x506c\n"
        ".inst.n 0x5828\n"
        ".inst.n 0xf110\n"
        ".inst.n 0x0f01\n"
        ".inst.n 0xd104\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd002\n"
        ".inst.n 0xf114\n"
        ".inst.n 0x0f01\n"
        ".inst.n 0xd101\n"
        ".inst.n 0x2000\n"
        ".inst.n 0xe04a\n"
        ".inst.n 0x0020\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfc34\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd120\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfbd3\n"
        ".inst.n 0x0780\n"
        ".inst.n 0xd50b\n"
        ".inst.n 0x9402\n"
        ".inst.n 0x48c7\n"
        ".inst.n 0x9001\n"
        ".inst.n 0xf240\n"
        ".inst.n 0x201a\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x4bc5\n"
        ".inst.n 0x4abb\n"
        ".inst.n 0x49bb\n"
        ".inst.n 0x2002\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfe18\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfbc3\n"
        ".inst.n 0x07c0\n"
        ".inst.n 0xd403\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfbbf\n"
        ".inst.n 0x0740\n"
        ".inst.n 0xd506\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F994_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f994(void)
{
    __asm__ volatile(
        ".inst.n 0x0780\n"
        ".inst.n 0xd50b\n"
        ".inst.n 0x9402\n"
        ".inst.n 0x48b7\n"
        ".inst.n 0x9001\n"
        ".inst.n 0xf240\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F9A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f9a0(void)
{
    __asm__ volatile(
        ".inst.n 0x201f\n"
        ".inst.n 0x9000\n"
        ".inst.n 0x4bb2\n"
        ".inst.n 0x4aa8\n"
        ".inst.n 0x49a8\n"
        ".inst.n 0x2003\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfdf2\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfb9d\n"
        ".inst.n 0x07c0\n"
        ".inst.n 0xd403\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfb99\n"
        ".inst.n 0x0740\n"
        ".inst.n 0xd506\n"
        ".inst.n 0x4aae\n"
        ".inst.n 0x0023\n"
        ".inst.n 0x0011\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x6044\n"
        ".inst.n 0xf6a5\n"
        ".inst.n 0xfa78\n"
        ".inst.n 0x2001\n"
        ".inst.n 0xbd3e\n"
        ".inst.n 0x4995\n"
        ".inst.n 0xf249\n"
        ".inst.n 0x5264\n"
        ".inst.n 0x5088\n"
        ".inst.n 0xf249\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055F9E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055f9e8(void)
{
    __asm__ volatile(
        ".inst.n 0x12d9\n"
        ".inst.n 0x5488\n"
        ".inst.n 0x4770\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x47f0\n"
        ".inst.n 0x0007\n"
        ".inst.n 0x000c\n"
        ".inst.n 0x4d82\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5604\n"
        ".inst.n 0x59a8\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd101\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfb6d\n"
        ".inst.n 0x0038\n"
        ".inst.n 0xb2c0\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd00d\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055FA0E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055fa0e(void)
{
    __asm__ volatile(
        ".inst.n 0xf44f\n"
        ".inst.n 0x4105\n"
        ".inst.n 0x5a68\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd008\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055FA18_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055fa18(void)
{
    __asm__ volatile(
        ".inst.n 0x5a68\n"
        ".inst.n 0x1e41\n"
        ".inst.n 0xb289\n"
        ".inst.n 0x0028\n"
        ".inst.n 0xf7ff\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055FA22_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055fa22(void)
{
    __asm__ volatile(
        ".inst.n 0xfb52\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x0803\n"
        ".inst.n 0xe01a\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x4705\n"
        ".inst.n 0x5be8\n"
        ".inst.n 0x2840\n"
        ".inst.n 0xdb0b\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5102\n"
        ".inst.n 0x5a68\n"
        ".inst.n 0x5a6a\n"
        ".inst.n 0x1c52\n"
        ".inst.n 0xf012\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055FA40_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055fa40(void)
{
    __asm__ volatile(
        ".inst.n 0x023f\n"
        ".inst.n 0x526a\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x0802\n"
        ".inst.n 0x2700\n"
        ".inst.n 0xe009\n"
        ".inst.n 0x5be9\n"
        ".inst.n 0x0028\n"
        ".inst.n 0xf7ff\n"
        ".inst.n 0xfb3a\n"
        ".inst.n 0x5be9\n"
        ".inst.n 0x1c49\n"
        ".inst.n 0x53e9\n"
        ".inst.n 0xf05f\n"
        ".inst.n 0x0802\n"
        ".inst.n 0x2700\n"
        ".inst.n 0xf44f\n"
        ".inst.n 0x7105\n"
        ".inst.n 0xb280\n"
        ".inst.n 0x4348\n"
        ".inst.n 0xeb05\n"
        ".inst.n 0x0900\n"
        ".inst.n 0x2200\n"
        ".inst.n 0x46ca\n"
        ".inst.n 0x4650\n"
        ".inst.n 0xf6a4\n"
        ".inst.n 0xfb47\n"
        ".inst.n 0x59a8\n"
        ".inst.n 0xf8c9\n"
        ".inst.n 0x020c\n"
        ".inst.n 0xb2ff\n"
        ".inst.n 0x2f00\n"
        ".inst.n 0xd00b\n"
        ".inst.n 0xf248\n"
        ".inst.n 0x5108\n"
        ".inst.n 0x5868\n"
        ".inst.n 0x2800\n"
        ".inst.n 0xd002\n"
        ".inst.n 0x5868\n"
        ".inst.n 0x1e40\n"
        ".inst.n 0xe000\n"
        ".inst.n 0x2000\n"
    );
}
#endif

#if defined(OPEN_CFW_AM125_0X0055FAA8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am125_0x0055faa8(void)
{
    __asm__ volatile(
        ".inst.n 0x2c00\n"
        ".inst.n 0xd001\n"
        ".inst.n 0xf884\n"
        ".inst.n 0x8000\n"
        ".inst.n 0x4648\n"
        ".inst.n 0xe8bd\n"
        ".inst.n 0x87f0\n"
        ".inst.n 0xe92d\n"
        ".inst.n 0x4ff8\n"
        ".inst.n 0xb084\n"
        ".inst.n 0x000c\n"
        ".inst.n 0x4e50\n"
        ".inst.n 0x2700\n"
        ".inst.n 0x2100\n"
        ".inst.n 0xf8ad\n"
        ".inst.n 0x100e\n"
        ".inst.n 0x2c00\n"
        ".inst.n 0xd002\n"
        ".inst.n 0xf64f\n"
    );
}
#endif
