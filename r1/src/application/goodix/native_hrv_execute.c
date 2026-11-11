#include <stdint.h>
#include <stddef.h>
#include "native_algorithm_state.h"
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_hook.h"
#include "goodix_hrv.h"
extern void __aeabi_memclr(void *,size_t);
/* Native0x20007c2c is initialized by the existing HRV initializer and then
 * caches the last HR record. Retain its canonical legacy owner name. */
extern volatile uint32_t r1_goodix_hrv_initialization_count;
_Static_assert(sizeof(goodix_hrv_input_rawdata)==56,"native HRV input");
_Static_assert(offsetof(goodix_hrv_input_rawdata,pst_module_unique)==52,"native unique slot");
_Static_assert(sizeof(goodix_hrv_result)==36,"native HRV result");
static uint32_t word(const void *p,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)p+offset);
}
static void result_word(const STGh3x2xFrameInfo *frame,uint32_t offset,uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)word(frame,0x3c)+offset)=value;
}
void GH3X2X_HrvAlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)result;(void)frame_id; /* Native0x2a65a is BX LR. */
}
GS8 GH3x2xHrvAlgoExe(const STGh3x2xFrameInfo *const frame)
{
    if (!frame) return -1;
    uint8_t enabled[4],gain[12];
    int32_t ppg[12];
    uint16_t drive[12];
    goodix_hrv_input_rawdata input;
    goodix_hrv_result result;
    __aeabi_memclr(ppg,sizeof(ppg));
    __aeabi_memclr(drive,sizeof(drive));
    __aeabi_memclr(gain,sizeof(gain));
    __aeabi_memclr(enabled,sizeof(enabled));
    __aeabi_memclr(&input,sizeof(input));
    __aeabi_memclr(&result,sizeof(result));
    uintptr_t frames=(uintptr_t)r1_goodix_algorithm_frame_table;
    const STGh3x2xFrameInfo *hr_frame=*(const STGh3x2xFrameInfo *const volatile *)(frames+4);
    uintptr_t hr_output=word(hr_frame,0x40);
    if (*(const volatile uint8_t *)hr_output)
        r1_goodix_hrv_initialization_count=word((const void *)hr_output,4);
    uint32_t unique=r1_goodix_hrv_initialization_count&255u;
    input.pst_module_unique=&unique;
    input.frame_id=*(const volatile uint8_t *)(uintptr_t)word(frame,0x38);
    input.total_ch_num=4;
    input.enable_flg=enabled;
    input.ppg_rawdata=ppg;
    input.ch_agc_gain=gain;
    input.ch_agc_drv=drive;
    input.acc_x=*(const volatile int16_t *)(uintptr_t)word(frame,0x18);
    input.acc_y=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+2);
    input.acc_z=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+4);
    input.sleep_flg=GH3x2xSleepFlagGet();
    input.bit_num=24;input.chip_type=1;input.data_type=0;
    for (uint32_t i=0;i<4;++i) {
        ppg[i]=(int32_t)word((const void *)(uintptr_t)word(frame,0x14),i*4);
        uint8_t previous=*(const volatile uint8_t *)((uintptr_t)word(frame,0x34)+i);
        uint8_t value=*(const volatile uint8_t *)((uintptr_t)word(frame,0x24)+i*4)&15u;
        if (previous!=value && previous!=255)
            *(volatile uint8_t *)((uintptr_t)word(frame,0x34)+i)=value;
        uint32_t agc=word((const void *)(uintptr_t)word(frame,0x24),i*4);
        drive[i]=(uint16_t)(((agc>>16)&255u)+((agc>>8)&255u));
        gain[i]=value;
        enabled[i/8]|=(uint8_t)(1u<<(7u-i%8));
    }
    uint32_t status=(uint32_t)goodix_hrv_calc(&input,&result);
    if (status==0) return 0;
    if (status!=GX_HRV_ALGO_UPDATE) return -5;
    *(volatile uint8_t *)(uintptr_t)word(frame,0x3c)=1;
    for (uint32_t i=0;i<4;++i) result_word(frame,4+i*4,(uint32_t)result.rri[i]);
    result_word(frame,20,(uint32_t)result.rri_confidence);
    result_word(frame,24,(uint32_t)result.rri_valid_num);
    *(volatile uint16_t *)((uintptr_t)word(frame,0x3c)+2)=127;
    uint8_t count=GH3x2x_BitCount(127);
    *(volatile uint8_t *)((uintptr_t)word(frame,0x3c)+1)=count;
    uint32_t frame_id=*(const volatile uint32_t *)(uintptr_t)word(frame,0x38);
    uintptr_t output=word(frame,0x3c);
    GH3X2X_HrvAlgorithmResultReport((STGh3x2xAlgoResult *)output,frame_id);
    return 0;
}
