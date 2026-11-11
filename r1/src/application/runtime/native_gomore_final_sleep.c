/* Native final sleep record serialization (0x8fa3c) and publication (0x4a704). */
#include <stdint.h>
#include <stddef.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern volatile uint8_t r1_temperature_sleep_capture[106];
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_sleep_drop_guard(const void *);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);

static uint16_t half(const volatile uint8_t *p)
{ return (uint16_t)(p[0]|(uint16_t)p[1]<<8); }
static uint32_t word(const volatile uint8_t *p)
{ return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24; }
static float real(const volatile uint8_t *p)
{
    union {uint32_t bits;float value;} v={.bits=word(p)};
    return v.value;
}
static uint32_t ring_enabled(void)
{ return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u); }

uint8_t *r1_gomore_final_sleep_record_serialize_native(const volatile void *workspace)
{
    const volatile uint8_t *in=(const volatile uint8_t *)workspace;
    const int8_t *stages=(const int8_t *)(uintptr_t)word(in+8);
    uint16_t count=half(in+16),runs=0;
    int32_t current=-1;
    uint8_t run_minus_one=0;
    uint8_t has_negative_stage=0;
    for (uint16_t i=0;i<count;i++) {
        uint8_t value=(uint8_t)stages[i];
        has_negative_stage|=(uint8_t)(value>>7);
        if ((uint32_t)value!=(uint32_t)current) {
            runs++;current=(int8_t)value;run_minus_one=0;
        }
        if (++run_minus_one>63u) {runs++;run_minus_one=0;}
    }
    if (ring_enabled())
        (void)r1_structured_log_format(0x0c400000,
            "[RING]stage_num:%d","[RING]stage_num:%d",runs);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"stage_num:%d",runs);

    /* The stock encoder emits a phantom first run for a signed stage byte
     * with its high bit set. Reserve that extra byte before writing it. */
    const size_t capacity=(size_t)runs+32u+
        (in[84]==1u && count!=0u && (uint8_t)stages[0]>=128u ? 1u : 0u);
    uint8_t *out=pvPortMalloc(capacity);
    if (!out) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x04000000,
                "[RING]sensor_malloc failed","[RING]sensor_malloc failed");
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0001,"sensor_malloc failed");
        return NULL;
    }
    __aeabi_memclr(out,capacity);

    uint16_t body_temperature=0;
    if (in[84]==1u) {
        uint16_t unscaled=0;
        body_temperature=gomore_primitives_stable_trimmed_median(
            (const uint16_t *)(const void *)(r1_temperature_sleep_capture+4),
            r1_temperature_sleep_capture[2],&unscaled);
        /* The native median provider writes the unscaled result to +104. */
        r1_temperature_sleep_capture[104]=(uint8_t)unscaled;
        r1_temperature_sleep_capture[105]=(uint8_t)(unscaled>>8);
    }
    gomore_primitives_final_sleep_record record={
        .wire_type=in[84],
        .start_timestamp=(int32_t)word(in),
        .end_timestamp=(int32_t)word(in+4),
        .stages=stages,
        .stage_count=count,
        .efficiency=real(in+40),
        .score=real(in+80),
        .rem_fraction=real(in+52),
        .light_fraction=real(in+56),
        .deep_fraction=real(in+60),
        .total_minutes=real(in+28),
        .wake_minutes=real(in+64),
        .rem_minutes=real(in+68),
        .light_minutes=real(in+72),
        .deep_minutes=real(in+76),
        .body_temperature=body_temperature,
    };
    size_t written=0;
    if (!gomore_primitives_final_sleep_record_serialize(
            &record,out,capacity,&written)) {
        vPortFree(out);
        return NULL;
    }
    if (in[84]==1u && has_negative_stage) {
        int32_t stage=(int8_t)stages[0],length_minus_one=-1;
        uint16_t encoded=0;
        for (uint16_t i=0;i<count;i++) {
            length_minus_one=(int8_t)(length_minus_one+1);
            uint8_t value=(uint8_t)stages[i];
            if ((uint32_t)value!=(uint32_t)stage || length_minus_one>62) {
                out[32u+encoded]=(uint8_t)((stage&3)|
                    ((length_minus_one&63)<<2));
                encoded++;
                stage=(int8_t)value;
                length_minus_one=0;
            }
            if (i==count-1u) {
                out[32u+encoded]=(uint8_t)((stage&3)|
                    (((length_minus_one+1)&63)<<2));
                encoded++;
            }
        }
        out[30]=(uint8_t)encoded;
        out[31]=(uint8_t)(encoded>>8);
    }
    return out;
}

void r1_gomore_final_sleep_record_publish_native(
    volatile uint32_t *count,volatile void *workspace)
{
    if (!count || !workspace) return;
    uint8_t *record=r1_gomore_final_sleep_record_serialize_native(workspace);
    if (!record) return;
    uint16_t stages=(uint16_t)(record[30]|(uint16_t)record[31]<<8);
    uint32_t start=word(record+12),end=word(record+16);
    const char *ring="[RING]type:%d, startTS:%d, endTS:%d, numStages:%d";
    if (ring_enabled())
        (void)r1_structured_log_format(0x0d000000,ring,ring,
            record[0],start,end,stages);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_4(0x001c0003,
            "type:%d, startTS:%d, endTS:%d, numStages:%d",
            record[0],start,end,stages);
    if (r1_sleep_drop_guard(record))
        (void)r1_event_publish(13,record,(uint16_t)(stages+32u));
    vPortFree(record);
}
