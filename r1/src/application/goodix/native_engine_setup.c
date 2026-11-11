#include <stdint.h>
#include <stddef.h>
#include "gh3x2x_demo_algorithm_calc.h"
#include "gh3x2x_demo_algo_config.h"
#include "gh3x2x_demo_algo_memory.h"
#include "goodix_hba.h"
#include "goodix_hrv.h"
#include "goodix_spo2.h"
#include "goodix_nadt.h"
volatile uint8_t r1_goodix_soft_adt_engine_flag
    __attribute__((section(".r1.goodix.soft.adt.engine.flag"),aligned(1)));

/* Numeric configuration records observed in the stock data sections. */
static const uint32_t nadt_defaults[15]={
    0x00030019,0x020404b0,0x008890ec,0x00862df4,25,1,300,0x008c0032,
    8,0x001e0032,15,1000,0x00640001,0x000a010c,0x0005000a
};
static void copy_bytes(void *destination,const void *source,uint32_t count)
{
    uint8_t *out=destination; const uint8_t *in=source;
    for (uint32_t i=0;i<count;++i) out[i]=in[i];
}
/* Capacity0 deliberately retains the native write to destination-1.
 * The normal engine callers pass20. No early-return guard is invented. */
static void interface_version(char *out,uint32_t capacity,const char *text,uint32_t size)
{
    uint32_t count=capacity<size ? capacity : size;
    copy_bytes(out,text,count);
    *(volatile uint8_t *)((uintptr_t)out+count-1u)=0;
}
const void *goodix_nadt_config_get_arr(void) { return nadt_defaults; }
void goodix_nadt_config_get_version(char *out,uint8_t capacity)
{ interface_version(out,capacity,"pv_v1.0.0",10); }
GU8 Gh3x2xGetHrAlgoSupportChnl(void) { return 4; }
GU8 Gh3x2xGetSpo2AlgoSupportChnl(void) { return 1; }
static uint32_t channel_count(const STAlgoChnlMap *map)
{
    return ((const volatile uint8_t *)map)[1];
}
_Static_assert(offsetof(STAlgoChnlMap,uchNum)==1,"native channel-count byte");
int32_t r1_goodix_hr_engine_init(uint32_t sample_rate)
{
    char version[120]={0},interface[20]={0}; uint32_t configuration[9];
    int32_t status=goodix_hba_version((uint8_t *)version);
    if (status) return status;
    GH3X2X_HbaAlgoChnlMapDefultSet();
    if (Gh3x2xGetHrAlgoSupportChnl()<channel_count(&g_stHbaAlgoChnlMap)) return 1;
    copy_bytes(configuration,goodix_hba_config_get_arr(),36);
    configuration[1]=sample_rate;
    configuration[2]=channel_count(&g_stHbaAlgoChnlMap);
    goodix_hba_config_get_version(interface,20);
    return goodix_hba_init(configuration,36,interface);
}
int32_t r1_goodix_hrv_engine_init(uint32_t sample_rate)
{
    char version[152]={0},interface[20]={0}; uint32_t configuration[6]={0};
    (void)goodix_hrv_version((uint8_t *)version);
    copy_bytes(configuration,goodix_hrv_config_get_arr(),24);
    configuration[1]=sample_rate;
    goodix_hrv_config_get_version(interface,20);
    return goodix_hrv_init(configuration,24,interface);
}
int32_t r1_goodix_spo2_engine_init(uint32_t sample_rate)
{
    char version[152]={0},interface[20]={0}; uint32_t configuration[19]={0};
    GH3X2X_Spo2AlgoChnlMapDefultSet();
    (void)goodix_spo2_version((uint8_t *)version);
    if (Gh3x2xGetSpo2AlgoSupportChnl()<channel_count(&g_stSpo2AlgoChnlMap)) return 1;
    copy_bytes(configuration,goodix_spo2_config_get_instance(),76);
    configuration[1]=sample_rate;
    configuration[0]=channel_count(&g_stSpo2AlgoChnlMap);
    goodix_spo2_config_get_version(interface,20);
    return goodix_spo2_init(configuration,76,interface);
}
void r1_goodix_soft_adt_engine_init(const STGh3x2xFrameInfo *frame)
{
    char version[120]={0},interface[20]={0};
    union { uint32_t words[15]; uint16_t halves[30]; } configuration={0};
    r1_goodix_soft_adt_engine_flag=0;
    (void)goodix_nadt_version((uint8_t *)version);
    copy_bytes(&configuration,goodix_nadt_config_get_arr(),60);
    uintptr_t rate=*(const volatile uint32_t *)((uintptr_t)frame+4);
    configuration.halves[0]=*(const volatile uint16_t *)rate;
    goodix_nadt_config_get_version(interface,20);
    (void)goodix_nadt_init(&configuration,60,interface);
}
