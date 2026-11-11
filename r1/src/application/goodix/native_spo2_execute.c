#include <stdint.h>
#include <stddef.h>
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_hook.h"
#include "goodix_spo2.h"
extern void __aeabi_memclr(void *,size_t);
_Static_assert(sizeof(goodix_spo2_input_rawdata)==56,"native SpO2 input");
_Static_assert(sizeof(goodix_spo2_result)==64,"native SpO2 result");
_Static_assert(offsetof(goodix_spo2_result,final_calc_flg)==48,"native update flag");
static uint32_t word(const void *p,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)p+offset);
}
static void publish_word(const STGh3x2xFrameInfo *frame,uint32_t offset,uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)word(frame,0x3c)+offset)=value;
}
void GH3X2X_Spo2AlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)result;(void)frame_id; /* Native0x2ad14 is BX LR. */
}
GS8 GH3x2xSpo2AlgoExe(const STGh3x2xFrameInfo *const frame)
{
    if (!frame) return -1;
    /* The assembler reads12 bytes through enable_flg: the four mask bytes
     * followed by the first two live PPG words. Keep one byte-addressable
     * object so that later PPG integrity writes remain visible there. */
    struct raw_packet {uint8_t enabled[4];int32_t ppg[12];} packet;
    _Static_assert(offsetof(struct raw_packet,ppg)==4,"native enable/PPG adjacency");
    _Static_assert(sizeof(struct raw_packet)==52,"native packet byte view");
    uint16_t drive[12];uint8_t gain[12];
    goodix_spo2_input_rawdata input;
    goodix_spo2_result result;
    __aeabi_memclr(packet.ppg,sizeof(packet.ppg));__aeabi_memclr(drive,sizeof(drive));
    __aeabi_memclr(gain,sizeof(gain));__aeabi_memclr(&packet,sizeof(packet.enabled));
    __aeabi_memclr(&input,sizeof(input));__aeabi_memclr(&result,sizeof(result));
    input.frame_id=*(const volatile uint8_t *)(uintptr_t)word(frame,0x38);
    input.total_ch_num=4;input.enable_flg=(uint8_t *)&packet;input.ppg_rawdata=packet.ppg;
    input.ch_agc_gain=gain;input.ch_agc_drv=drive;
    input.acc_x=*(const volatile int16_t *)(uintptr_t)word(frame,0x18);
    input.acc_y=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+2);
    input.acc_z=*(const volatile int16_t *)((uintptr_t)word(frame,0x18)+4);
    input.sleep_flg=GH3x2xSleepFlagGet();
    input.bit_num=24;input.chip_type=1;input.data_type=0;
    for (uint32_t i=0;i<12;++i) {
        uint32_t index=((const volatile uint8_t *)&g_stSpo2AlgoChnlMap)[3+i+(i&~3u)];
        if (index<255) {
            uint32_t agc=word((const void *)(uintptr_t)word(frame,0x24),index*4);
            drive[i]=(uint16_t)(((agc>>16)&255u)+((agc>>8)&255u));
            gain[i]=*(const volatile uint8_t *)((uintptr_t)word(frame,0x24)+index*4)&15u;
            packet.enabled[i/8]|=(uint8_t)(1u<<(7u-i%8));
            packet.ppg[i]=(int32_t)word((const void *)(uintptr_t)word(frame,0x14),index*4);
        }
    }
    uint32_t status=(uint32_t)goodix_spo2_calc(&input,&result);
    if (status!=0 && status!=3 && status!=4) return -5;
    if (result.final_calc_flg!=1) return 0;
    *(volatile uint8_t *)(uintptr_t)word(frame,0x3c)=1;
    /* Signed input bounds keep the rounded result within int32. Preserve
     * native conversion/division order and the existing finite-domain round. */
    float scaled=(float)result.final_spo2/10000.0f;
    publish_word(frame,4,(uint32_t)GH3x2x_Round(scaled));
    publish_word(frame,8,(uint32_t)result.final_r_val);
    publish_word(frame,12,(uint32_t)result.final_confi_coeff);
    publish_word(frame,16,(uint32_t)result.final_valid_level);
    publish_word(frame,20,(uint32_t)result.final_hb_mean);
    publish_word(frame,24,(uint32_t)result.final_invalidFlg);
    uintptr_t output=word(frame,0x3c);
    *(volatile uint32_t *)(output+28)=word((const void *)output,4);
    *(volatile uint16_t *)((uintptr_t)word(frame,0x3c)+2)=255;
    uint8_t count=GH3x2x_BitCount(255);
    *(volatile uint8_t *)((uintptr_t)word(frame,0x3c)+1)=count;
    uint32_t frame_id=*(const volatile uint32_t *)(uintptr_t)word(frame,0x38);
    output=word(frame,0x3c);
    GH3X2X_Spo2AlgorithmResultReport((STGh3x2xAlgoResult *)output,frame_id);
    return 0;
}
