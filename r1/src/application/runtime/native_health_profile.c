/* R1 stock 6c640, 735e0, 6abf8: cached profile extraction and validation. */
#include "native_health_profile.h"
#include "../board/native_kv_class.h"
extern void *volatile r1_health_settings_kv_handle;
uint32_t r1_record12_validate(const volatile uint8_t *record)
{
    uint32_t value=record[0];
    if (value<=10 || value>=100) return 0;
    if (record[1]>1) return 0;
    value=record[2];
    if (value<=100 || value>=220) return 0;
    value=record[3];
    return value>30 && value<150;
}
uint32_t r1_health_profile_features(const volatile uint8_t *record,volatile float *out)
{
    out[0]=(float)record[0];
    out[1]=record[1]==1 ? 1.0f:0.0f;
    out[2]=(float)record[2];
    out[3]=(float)record[3];
    for (unsigned i=0;i<3;++i) {
        int16_t value=((const volatile int16_t *)record)[i+2];
        out[i+4]=value==0 ? -1.0f:(float)value;
    }
    return r1_record12_validate(record);
}
struct __attribute__((packed,may_alias)) r1_health_profile_word { uint32_t value; };
uint64_t r1_kv_health_get(void *out,uint32_t seed0,uint32_t seed1,uint32_t seed2)
{
    if (!out) return (uint64_t)seed0<<32;
    uint32_t record[3]={seed0,seed1,seed2};
    (void)r1_kv_class_read(r1_health_settings_kv_handle,record,12);
    volatile struct r1_health_profile_word *destination=out;
    destination[0].value=record[0];
    destination[1].value=record[1];
    destination[2].value=record[2];
    return ((uint64_t)record[0]<<32)|record[2];
}
uint64_t r1_health_lifecycle_profile_native(void *out,uint32_t seed0,uint32_t seed1,uint32_t seed2)
{
    if (!out) return (uint64_t)seed0<<32;
    uint32_t record[3]={seed0,seed1,seed2};
    (void)r1_kv_health_get(record,seed0,seed1,seed2);
    uint32_t valid=r1_health_profile_features((const volatile uint8_t *)record,out);
    return ((uint64_t)record[0]<<32)|valid;
}
