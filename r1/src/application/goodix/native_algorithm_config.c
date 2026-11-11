#include <stdint.h>
#include <stddef.h>
#include "native_algorithm_state.h"
#include "gh3x2x_demo_algo_call.h"
#include "gh3x2x_demo_algo_memory.h"
#include "gh3x2x_demo_algo_config.h"
#include "goodix_mem.h"
extern void GH3X2X_LoadGoodixAlgoRegConfigArr(const STGh3x2xInitConfig *);
/* Shared native algorithm state. Future lifecycle entries must use these
 * owners rather than introducing separate frame or memory cells. */
const STGh3x2xFrameInfo *const *volatile r1_goodix_algorithm_frame_table
    __attribute__((section(".r1.goodix.algorithm.frames"),aligned(4)));
volatile struct r1_goodix_algorithm_memory r1_goodix_algorithm_memory
    __attribute__((section(".r1.goodix.algorithm.memory"),aligned(4)));
_Static_assert(sizeof(struct r1_goodix_algorithm_memory)==12,"native memory state");
_Static_assert(offsetof(struct r1_goodix_algorithm_memory,pool)==4,"native pool cell");
_Static_assert(offsetof(struct r1_goodix_algorithm_memory,size)==8,"native size cell");
GU32 r1_goodix_algorithm_pool[0x7540/4]
    __attribute__((section(".bss.r1.goodix.algorithm.pool"),aligned(4)));
const STGh3x2xReg r1_goodix_algorithm_registers0[48] __attribute__((section(".r1.goodix.algorithm.list0"),aligned(2)))={
    {0x33c0,0x0000},
    {0x33c2,0x0000},
    {0x33c4,0x0000},
    {0x33c6,0x0000},
    {0x33c8,0x0000},
    {0x33ca,0x0000},
    {0x33cc,0x0000},
    {0x33ce,0x0000},
    {0x33d0,0x0000},
    {0x33d2,0x0000},
    {0x35c0,0x0002},
    {0x35c4,0x0100},
    {0x36c0,0x0000},
    {0x36c2,0x0000},
    {0x36c4,0x0020},
    {0x36c6,0x0000},
    {0x36c8,0x0010},
    {0x36ca,0x0000},
    {0x36cc,0x0003},
    {0x36ce,0x0000},
    {0x36d0,0x0003},
    {0x36d2,0x0000},
    {0x42c0,0x846c},
    {0x42c2,0xfffd},
    {0x42c4,0x87e3},
    {0x42c6,0xffff},
    {0x42c8,0xcc38},
    {0x42ca,0x000f},
    {0x42cc,0x0001},
    {0x42ce,0x0000},
    {0x42d0,0x0000},
    {0x42d2,0x0000},
    {0x42d4,0x001e},
    {0x42d6,0x0000},
    {0x42d8,0x000f},
    {0x42da,0x0000},
    {0x42dc,0x0004},
    {0x42de,0x0000},
    {0x42e0,0x0003},
    {0x42e2,0x0000},
    {0x42e4,0x0000},
    {0x42e6,0x0000},
    {0x42e8,0x0000},
    {0x42ea,0x0000},
    {0x44c0,0x0001},
    {0x44cc,0xff01},
    {0x44d4,0xff00},
    {0xffff,0x0001},
};
const STGh3x2xReg r1_goodix_algorithm_registers1[1] __attribute__((section(".r1.goodix.algorithm.list1"),aligned(2)))={
    {0xffff,0x0001},
};
const STGh3x2xReg r1_goodix_algorithm_registers2[1] __attribute__((section(".r1.goodix.algorithm.list2"),aligned(2)))={
    {0xffff,0x0001},
};
const STGh3x2xReg r1_goodix_algorithm_registers3[1] __attribute__((section(".r1.goodix.algorithm.list3"),aligned(2)))={
    {0x0000,0x0000},
};
const STGh3x2xInitConfig g_stGoodixAlgoCfgListArr[4]
    __attribute__((section(".r1.goodix.algorithm.configurations"),aligned(4)))={
    {r1_goodix_algorithm_registers0,48},
    {r1_goodix_algorithm_registers1,1},
    {r1_goodix_algorithm_registers2,1},
    {r1_goodix_algorithm_registers3,1},
};
GS8 GH3X2X_AlgoMemInit(void)
{
    if (r1_goodix_algorithm_memory.initialized) return 0;
    GU32 size=r1_goodix_algorithm_memory.size;
    r1_goodix_algorithm_memory.pool=r1_goodix_algorithm_pool;
    if (!size || goodix_mem_init(r1_goodix_algorithm_pool,(int32_t)size)!=0) return -5;
    r1_goodix_algorithm_memory.initialized=1;
    return 0;
}
GS8 GH3X2X_AlgoMemConfig(GU32 size)
{
    if (!size) return -5;
    (void)GH3X2X_AlgoDeinit(UINT32_MAX);
    r1_goodix_algorithm_memory.size=size;
    return GH3X2X_AlgoMemInit();
}
void GH3X2X_AlgoCallConfigInit(const STGh3x2xFrameInfo *const frames[],GU8 index)
{
    if (frames) r1_goodix_algorithm_frame_table=frames;
    (void)GH3X2X_AlgoMemConfig(0x7540);
    if (index<4u) GH3X2X_LoadGoodixAlgoRegConfigArr(&g_stGoodixAlgoCfgListArr[index]);
}
