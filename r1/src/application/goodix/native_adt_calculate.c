#include <stdint.h>
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_hook.h"
#include "native_nadt_state.h"
/* Native cached sample0x20007c28 and six-word filter0x2003778c. The three
 * status/count bytes remain owned by native_adt_teardown.c. */
volatile uint32_t r1_goodix_native_adt_raw
    __attribute__((section(".r1.goodix.native.adt.raw"),aligned(4)));
volatile uint32_t r1_goodix_native_adt_history[6]
    __attribute__((section(".r1.goodix.native.adt.history"),aligned(4)));
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t frame_word(const STGh3x2xFrameInfo *frame,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)frame+offset);
}
GU8 Gh3x2xMovingAvaFilter(GU32 *data,GU8 bypass)
{
    if (bypass) return 1;
    uint32_t count=r1_goodix_native_adt_flags[2];
    if (count>=6) {
        for (uint32_t i=1;i<6;++i)
            r1_goodix_native_adt_history[i-1]=r1_goodix_native_adt_history[i];
        count=5;
        r1_goodix_native_adt_flags[2]=5;
    }
    r1_goodix_native_adt_history[count]=*(volatile GU32 *)data;
    ++count;
    r1_goodix_native_adt_flags[2]=(uint8_t)count;
    if (count>1) {
        uint32_t sum=0;
        for (uint32_t i=0;i<count-1;++i) sum+=r1_goodix_native_adt_history[i];
        *(volatile GU32 *)data=sum/(count-1);
    }
    return 1;
}
void GH3X2X_AdtAlgorithmResultReport(STGh3x2xAlgoResult *result,GU32 frame_id)
{
    (void)frame_id;
    volatile uint8_t *bytes=(volatile uint8_t *)result;
    if (!bytes[0]) return;
    uint32_t value=*(const volatile uint32_t *)(bytes+4);
    if (value==1) {
        GH3X2X_ClearSoftEvent(0x20);
        GH3X2X_SetSoftEvent(0x10);
    } else if (value==2) {
        GH3X2X_ClearSoftEvent(0x10);
        GH3X2X_SetSoftEvent(0x20);
    }
}
static void wear_event(const STGh3x2xFrameInfo *frame,
    const volatile uint32_t *filtered,uint32_t difference,uint32_t on)
{
    static const char ring_on[]="[RING]wear on event, Rawdata = %d, unRawdataDiff = %d";
    static const char ring_off[]="[RING]wear off event, Rawdata = %d, unRawdataDiff = %d";
    static const char plain_on[]="wear on event, Rawdata = %d, unRawdataDiff = %d";
    static const char plain_off[]="wear off event, Rawdata = %d, unRawdataDiff = %d";
    r1_goodix_native_adt_flags[0]=(uint8_t)on;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        const char *format=on?ring_on:ring_off;
        (void)r1_structured_log_format(0x0c800000,format,format,*filtered,(int32_t)difference);
    }
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,on?plain_on:plain_off,*filtered,difference);
    *(volatile uint8_t *)(uintptr_t)frame_word(frame,0x3c)=1;
    *(volatile uint32_t *)((uintptr_t)frame_word(frame,0x3c)+4)=on?1:2;
}
GS8 GH3x2xAdtAlgoExe(const STGh3x2xFrameInfo *const frame)
{
    volatile GU32 filtered=*(const volatile GU32 *)(uintptr_t)frame_word(frame,0x14);
    uint32_t original=*(const volatile GU32 *)(uintptr_t)frame_word(frame,0x14);
    (void)Gh3x2xMovingAvaFilter((GU32 *)&filtered,0);
    *(volatile uint32_t *)((uintptr_t)frame_word(frame,0x3c)+4)=0;
    uint32_t difference=original-filtered;
    r1_goodix_native_adt_raw=filtered;
    if (!r1_goodix_native_adt_flags[1]) {
        if (original>0x845f7cu && (int32_t)difference>-8000000)
            wear_event(frame,&filtered,difference,1);
        else if (original<0x842024u)
            wear_event(frame,&filtered,difference,0);
        r1_goodix_native_adt_flags[1]=1;
    }
    uint8_t wear=r1_goodix_native_adt_flags[0];
    if (!wear) {
        if (original>0x845f7cu && (int32_t)difference>-8000000)
            wear_event(frame,&filtered,difference,1);
    } else if (wear==1 && original<0x842024u)
        wear_event(frame,&filtered,difference,0);
    *(volatile uint16_t *)((uintptr_t)frame_word(frame,0x3c)+2)=7;
    uint8_t count=GH3x2x_BitCount(7);
    *(volatile uint8_t *)((uintptr_t)frame_word(frame,0x3c)+1)=count;
    *(volatile uint32_t *)((uintptr_t)frame_word(frame,0x3c)+8)=difference;
    uint32_t counter=*(const volatile uint32_t *)(uintptr_t)frame_word(frame,0x38);
    *(volatile uint32_t *)((uintptr_t)frame_word(frame,0x3c)+12)=counter;
    counter=*(const volatile uint32_t *)(uintptr_t)frame_word(frame,0x38);
    GH3X2X_AdtAlgorithmResultReport((STGh3x2xAlgoResult *)(uintptr_t)frame_word(frame,0x3c),counter);
    return 0;
}
