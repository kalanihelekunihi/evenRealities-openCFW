#include <stdint.h>
/* Owner-authorized native temperature contracts; GXT transport/mode and NV providers are reused. */
uint8_t r1_temperature_calibration[6] __attribute__((section(".r1.temp.calibration"),aligned(1)))={0};
const char r1_temp_text_6f798[52] __attribute__((section(".r1.temp.s6f798")))="[RING][GXT310] Trigger one-shot failed, addr=0x%02X";
const char r1_temp_text_6f7d4[48] __attribute__((section(".r1.temp.s6f7d4")))="[GXT310] Trigger one-shot failed, addr=0x%02X";
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern void r1_gxt310_disable_pair_native(void);
extern int32_t osDelay(uint32_t ticks);
uint32_t r1_gxt310_one_shot_channel0(void),r1_gxt310_one_shot_channel2(void);
uint32_t r1_gxt310_temperature_channel0(void),r1_gxt310_temperature_channel2(void);
uint32_t r1_temperature_calibration_read(void *destination);
uint32_t r1_gxt310_one_shot(uint32_t address);
uint32_t r1_gxt310_temperature_read(uint32_t address);
struct __attribute__((packed,may_alias)) r1_temperature_unaligned_halfword {
    uint16_t value;
};
static uint16_t calibration_halfword(const volatile uint8_t *bytes)
{
    return ((const volatile struct r1_temperature_unaligned_halfword *)
            (const volatile void *)bytes)->value;
}
/* Native 0x50e4c: preserve the channel sequence and modulo-32-bit arithmetic.
 * Calibration uses live byte/halfword loads, including the unaligned +1 load.
 * Adding the sign bit before extracting bits 1..16 matches native rounding. */
uint32_t r1_temperature_pair_read_calibrated(void)
{
    r1_gxt310_bus_acquire();
    (void)r1_gxt310_enable_pair_native();
    (void)r1_gxt310_one_shot_channel0();
    (void)r1_gxt310_one_shot_channel2();
    (void)osDelay(80);
    uint32_t first=r1_gxt310_temperature_channel0();
    uint32_t second=r1_gxt310_temperature_channel2();
    r1_gxt310_disable_pair_native();
    r1_gxt310_bus_release();
    (void)r1_temperature_calibration_read(r1_temperature_calibration);
    const volatile uint8_t *calibration=r1_temperature_calibration;
    for (uint32_t i=0;i<6;i++) {
        if (calibration[i]==UINT8_MAX) continue;
        uint8_t mode=calibration[0];
        if (mode==0) first-=calibration_halfword(calibration+1);
        else if (mode==1) first+=calibration_halfword(calibration+1);
        mode=calibration[3];
        if (mode==0) second-=calibration_halfword(calibration+4);
        else if (mode==1) second+=calibration_halfword(calibration+4);
        break;
    }
    uint32_t sum=first+second;
    return ((sum+(sum>>31))>>1)&UINT16_MAX;
}
extern uint32_t r1_gxt310_transfer_read_native(uint32_t address,uint32_t reg,
                                              void *destination,uint32_t size);
/* Native conversion with an explicit zeroed transfer word; scratch R3 is not a C result. */
__attribute__((noinline,used)) uint32_t
r1_gxt310_temperature_read_body(uint32_t address,volatile uint32_t *frame)
{
    *frame=0;
    (void)r1_gxt310_transfer_read_native(address,0,(void *)frame,2);
    uint32_t raw=__builtin_bswap16(calibration_halfword(
        (const volatile uint8_t *)frame));
    int32_t sample=(int32_t)raw;
    if (raw&0x8000u) sample-=65536;
    float scaled=(float)sample*0.0078125f;
    return (uint32_t)(int32_t)(scaled*1000.0f);
}
__attribute__((noinline)) uint32_t r1_gxt310_temperature_read(uint32_t address)
{
    volatile uint32_t frame;
    return r1_gxt310_temperature_read_body(address,&frame);
}
uint32_t r1_gxt310_temperature_channel0(void) { return r1_gxt310_temperature_read(0x90); }
uint32_t r1_gxt310_temperature_channel2(void) { return r1_gxt310_temperature_read(0x94); }
extern uint32_t r1_gxt310_transfer_write_native(uint32_t address,uint32_t reg,
                                               const void *source,uint32_t size);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
/* Native trigger command and logging policy, with an ordinary C transfer word. */
__attribute__((noinline,used)) uint32_t
r1_gxt310_one_shot_body(uint32_t address,volatile uint32_t *frame)
{
    *frame=0x0000c101u;
    if (r1_gxt310_transfer_write_native(address,1,(const void *)frame,2))
        return 1;
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04400000u,r1_temp_text_6f798,
                                     r1_temp_text_6f798,address);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0001u,r1_temp_text_6f7d4,address);
    return 0;
}
__attribute__((noinline)) uint32_t r1_gxt310_one_shot(uint32_t address)
{
    volatile uint32_t frame;
    return r1_gxt310_one_shot_body(address,&frame);
}
uint32_t r1_gxt310_one_shot_channel0(void) { return r1_gxt310_one_shot(0x90); }
uint32_t r1_gxt310_one_shot_channel2(void) { return r1_gxt310_one_shot(0x94); }
extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
struct __attribute__((packed,may_alias)) r1_temperature_unaligned_word {
    uint32_t value;
};
/* Cached-class extraction requires a valid fully populated 124-byte nv_r1
 * record. Keep ordered stores; private stack aliases are outside the C ABI. */
__attribute__((noinline,used)) uint32_t
r1_temperature_calibration_read_body(void *destination,volatile uint8_t *record)
{
    (void)r1_kv_class_read(r1_device_info_kv_handle,(void *)record,124);
    uint32_t word=((const volatile struct r1_temperature_unaligned_word *)
                  (const volatile void *)(record+62))->value;
    ((volatile struct r1_temperature_unaligned_word *)destination)->value=word;
    uint32_t halfword=calibration_halfword(record+66);
    ((volatile struct r1_temperature_unaligned_halfword *)
     ((volatile uint8_t *)destination+4))->value=(uint16_t)halfword;
    return halfword;
}
__attribute__((noinline)) uint32_t r1_temperature_calibration_read(void *destination)
{
    _Alignas(4) volatile uint8_t record[124];
    return r1_temperature_calibration_read_body(destination,record);
}
