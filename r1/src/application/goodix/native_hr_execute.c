#include <stdint.h>
#include <stddef.h>
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_hook.h"
#include "goodix_hba.h"
extern void __aeabi_memclr(void *,size_t);
_Static_assert(sizeof(goodix_hba_input_rawdata)==56,"native HBA input");
_Static_assert(sizeof(goodix_hba_result)==40,"native HBA output");
_Static_assert(offsetof(STAlgoChnlMap,uchAlgoChnlMap)==3,"native channel map");
static uint32_t word(const void *p,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)p+offset);
}
static void publish_word(const STGh3x2xFrameInfo *frame,uint32_t offset,uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)word(frame,0x3c)+offset)=value;
}
void GH3X2X_HrAlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)result;(void)frame_id; /* Native0x2a658 is BX LR. */
}
GS8 GH3x2xHrAlgoExe(const STGh3x2xFrameInfo *const frame)
{
    if (!frame) return -1;
    uint8_t enabled[4],gain[12];
    int32_t ppg[12];
    uint16_t drive[12];
    goodix_hba_input_rawdata input;
    goodix_hba_result result;
    __aeabi_memclr(ppg,sizeof(ppg));
    __aeabi_memclr(drive,sizeof(drive));
    __aeabi_memclr(gain,sizeof(gain));
    __aeabi_memclr(enabled,sizeof(enabled));
    __aeabi_memclr(&input,sizeof(input));
    __aeabi_memclr(&result,sizeof(result));
    uint32_t unique=*(const volatile uint8_t *)&g_unHrParamsArr[1];
    input.pst_module_unique=&unique;
    input.frame_id=*(const volatile uint8_t *)(uintptr_t)word(frame,0x38);
    input.total_ch_num=4;input.enable_flg=enabled;input.ppg_rawdata=ppg;
    input.ch_agc_gain=gain;input.ch_agc_drv=drive;
    input.acc_x=*(const volatile int16_t *)(uintptr_t)word(frame,0x18);
    input.acc_y=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+2);
    input.acc_z=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+4);
    input.sleep_flg=GH3x2xSleepFlagGet();
    input.bit_num=24;input.chip_type=1;input.data_type=0;
    for (uint32_t i=0;i<12;++i) {
        uint32_t index=((const volatile uint8_t *)&g_stHbaAlgoChnlMap)[3+i+(i&~3u)];
        if (index<255) {
            enabled[i/8]|=(uint8_t)(1u<<(7u-i%8));
            ppg[i]=(int32_t)word((const void *)(uintptr_t)word(frame,0x14),index*4);
        }
    }
    uint32_t status=(uint32_t)goodix_hba_calc(&input,&result);
    /* Native invokes this even on a failed calculation and inspects the
     * result only afterward. It is not interchangeable with a debug no-op. */
    goodix_hba_essential_info_print(&input);
    if (status) return -5;
    if (result.hba_out_flag!=1) return 0;
    *(volatile uint8_t *)(uintptr_t)word(frame,0x3c)=1;
    publish_word(frame,4,result.hba_out);
    publish_word(frame,8,result.valid_score);
    publish_word(frame,12,result.hba_snr*100u);
    publish_word(frame,16,result.valid_level);
    publish_word(frame,20,result.hba_acc_info);
    publish_word(frame,24,result.hba_reg_scence);
    *(volatile uint16_t *)((uintptr_t)word(frame,0x3c)+2)=63;
    uint8_t count=GH3x2x_BitCount(63);
    *(volatile uint8_t *)((uintptr_t)word(frame,0x3c)+1)=count;
    uint32_t frame_id=*(const volatile uint32_t *)(uintptr_t)word(frame,0x38);
    uintptr_t output=word(frame,0x3c);
    GH3X2X_HrAlgorithmResultReport((STGh3x2xAlgoResult *)output,frame_id);
    *(volatile uint8_t *)(uintptr_t)word(frame,0x40)=(uint8_t)result.hba_out_flag;
    *(volatile uint32_t *)((uintptr_t)word(frame,0x40)+4)=result.hba_out;
    return 0;
}
