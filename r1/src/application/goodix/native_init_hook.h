/* R1 init hook 0x6a500. Watermark backup is cleared even while reset
 * recovery suppresses algorithm reconfiguration. The upstream default
 * disables this word together with its optional ADT watermark policy. */
#ifndef R1_NATIVE_INIT_HOOK_H
#define R1_NATIVE_INIT_HOOK_H
GU16 g_usCurrentConfigListFifoWmBak
    __attribute__((section(".r1.goodix.fifo.watermark.backup"),aligned(2)))=0;
void gh3x2x_init_hook_func(void)
{
    *(volatile GU16 *)&g_usCurrentConfigListFifoWmBak=0;
    if (GH3x2x_GetChipResetRecoveringFlag()==0)
        GH3X2X_AlgoCallConfigInit(g_pstGh3x2xFrameInfo,g_uchGh3x2xRegCfgArrIndex);
}
#endif
