#include <stdint.h>
#include <stddef.h>
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_hook.h"
#include "goodix_nadt.h"
#include "native_nadt_state.h"
extern void __aeabi_memclr(void *,size_t);
extern volatile uint8_t r1_goodix_soft_adt_initialization_flags[2];
/* Native RW cells0x20007c14 and0x20007c48. All other state owners are shared
 * with existing configuration/init/deinit code. */
GU8 g_SoftAdtWearState __attribute__((section(".r1.goodix.soft.adt.report.state"),aligned(1)))=0;
volatile uint32_t r1_goodix_soft_adt_timeout_seconds
    __attribute__((section(".r1.goodix.soft.adt.timeout.seconds"),aligned(4)))=30;
_Static_assert(sizeof(goodix_nadt_input_rawdata)==56,"native soft ADT input");
_Static_assert(sizeof(goodix_nadt_input_unique)==24,"native soft ADT unique input");
_Static_assert(sizeof(goodix_nadt_result)==24,"native soft ADT result");
static uint32_t word(const void *p,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)p+offset);
}
static uint8_t cap_enabled(void)
{
    return *(const volatile GU8 *)&g_uchAlgoCapEnable;
}
static void soft_report(const STGh3x2xAlgoResult *result)
{
    uint32_t value=word(result,4);
    uint8_t previous=*(volatile GU8 *)&g_SoftAdtWearState;
    if (value==1 && previous!=1) {
        GH3X2X_ClearSoftEvent(2);
        GH3X2X_SetSoftEvent(8);
        *(volatile GU8 *)&g_SoftAdtWearState=1;
    } else if ((value&2u) && previous!=2) {
        GH3X2X_ClearSoftEvent(8);
        GH3X2X_SetSoftEvent(2);
        *(volatile GU8 *)&g_SoftAdtWearState=2;
    }
}
void GH3X2X_SoftAdtGreenAlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)frame_id;soft_report(result);
}
void GH3X2X_SoftAdtIrAlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)frame_id;soft_report(result);
}
GS8 GH3x2xSoftAdtAlgoExe(const STGh3x2xFrameInfo *const frame)
{
    if (!frame) return -1;
    int32_t ppg[12],ipd[12],cap[4],cap_enable[4];
    uint8_t gain[12],enabled[4];
    uint16_t drive[12];
    goodix_nadt_input_rawdata input;
    goodix_nadt_input_unique unique;
    goodix_nadt_result result;
    __aeabi_memclr(ppg,sizeof(ppg));__aeabi_memclr(ipd,sizeof(ipd));
    __aeabi_memclr(cap,sizeof(cap));__aeabi_memclr(cap_enable,sizeof(cap_enable));
    __aeabi_memclr(gain,sizeof(gain));__aeabi_memclr(enabled,sizeof(enabled));
    __aeabi_memclr(drive,sizeof(drive));__aeabi_memclr(&input,sizeof(input));
    __aeabi_memclr(&unique,sizeof(unique));__aeabi_memclr(&result,sizeof(result));
    unique.ppg_colour_flg=r1_goodix_soft_adt_initialization_flags[1];
    unique.cap_rawdata=cap;unique.cap_enable_flg=cap_enable;unique.ch_ipd=ipd;
    if (cap_enabled()==1) {
        unique.cap_channel_num=4;
        for (uint32_t i=0;i<4;++i) {
            cap[i]=(int32_t)word((const void *)(uintptr_t)word(frame,0x1c),i*4);
            cap_enable[i]=1;
        }
    }
    input.pst_module_unique=&unique;
    input.frame_id=*(const volatile uint8_t *)(uintptr_t)word(frame,0x38);
    input.total_ch_num=4;input.enable_flg=enabled;input.ppg_rawdata=ppg;
    input.ch_agc_gain=gain;input.ch_agc_drv=drive;
    input.acc_x=*(const volatile int16_t *)(uintptr_t)word(frame,0x18);
    input.acc_y=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+2);
    input.acc_z=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+4);
    input.sleep_flg=GH3x2xSleepFlagGet();
    input.bit_num=24;input.chip_type=1;input.data_type=0;
    for (uint32_t i=0;i<3;++i) {
        ppg[i*4]=(int32_t)word((const void *)(uintptr_t)word(frame,0x14),i*4);
        uint32_t agc=word((const void *)(uintptr_t)word(frame,0x24),i*4);
        drive[i*4]=(uint16_t)(((agc>>16)&255u)+((agc>>8)&255u));
        gain[i*4]=*(const volatile uint8_t *)((uintptr_t)word(frame,0x24)+i*4)&15u;
    }
    uint32_t status=(uint32_t)goodix_nadt_calc(&input,&result);
    uint32_t threshold=r1_goodix_soft_adt_timeout_seconds*
        *(const volatile uint16_t *)(uintptr_t)word(frame,4);
    if (r1_goodix_native_soft_adt_timeout>=threshold && !((uint32_t)result.nadt_out&3u)) {
        result.nadt_out=(int32_t)((uint32_t)result.nadt_out|1u);
        r1_goodix_native_soft_adt_timeout=0;
    }
    if (!((uint32_t)result.nadt_out&2u) && word(frame,0)==0x8000u)
        r1_goodix_native_soft_adt_timeout=r1_goodix_native_soft_adt_timeout+1u;
    if (status) return -5;
    if (cap_enabled()==1 || result.nadt_out_flag!=1) return 0;
    *(volatile uint8_t *)(uintptr_t)word(frame,0x3c)=1;
    *(volatile uint16_t *)((uintptr_t)word(frame,0x3c)+2)=3;
    uint8_t count=GH3x2x_BitCount(3);
    *(volatile uint8_t *)((uintptr_t)word(frame,0x3c)+1)=count;
    *(volatile uint32_t *)((uintptr_t)word(frame,0x3c)+4)=(uint32_t)result.nadt_out;
    *(volatile uint32_t *)((uintptr_t)word(frame,0x3c)+8)=(uint32_t)result.nadt_confi;
    uint8_t colour=r1_goodix_soft_adt_initialization_flags[1];
    if (colour==0 || colour==1) {
        uint32_t frame_id=*(const volatile uint8_t *)(uintptr_t)word(frame,0x38);
        STGh3x2xAlgoResult *output=(STGh3x2xAlgoResult *)(uintptr_t)word(frame,0x3c);
        if (!colour) GH3X2X_SoftAdtGreenAlgorithmResultReport(output,frame_id);
        else GH3X2X_SoftAdtIrAlgorithmResultReport(output,frame_id);
    }
    return 0;
}
