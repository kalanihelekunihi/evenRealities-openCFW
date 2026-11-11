/* Stock 0x62c30 and its fifteen startup-initialized callback entries.
 * The stock compressed RW table has 72 slots, 15 of them nonzero. */
#include <stdint.h>
#include <stddef.h>
#include "../runtime/native_factory_mode.h"
#include "native_battery_context.h"

extern uint32_t r1_legacy_bounded_reply_send(const void *,uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_motion_refresh_selection(void),r1_nfc_chip_id_probe(void);
extern uint32_t r1_yhm_status_byte_get(volatile uint8_t *);
extern uint8_t r1_goodix_identity_probe(void);
extern uint32_t r1_gxt310_temp_average_read(void),r1_touch_chip_id_probe(void);
extern void r1_temperature_pair_read(volatile uint16_t *);
extern void r1_gxt310_id_pair_read(volatile uint8_t *);
extern void r1_temperature_pair_reduce(volatile void *);
extern uint32_t r1_battery_runtime_update_service(void);
extern void r1_goodix_stop_stock_profiles(void),r1_goodix_start_profile_4000(void),r1_goodix_start_profile_2000(void);
extern uint32_t r1_kv_nv_r1_byte_set_c(uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_reset_trace_persist_tag_write(uint32_t);
extern _Noreturn void r1_manager_system_reset(void);
extern void r1_sysctl_op_sequence_thunk(void);

/* Native factory state word at 0x20006c50, immediately after the existing
 * 28-byte prefix. Only the stream handle is owned by this new variable. */
volatile uint32_t r1_factory_gray_stream_handle
    __attribute__((section(".r1.factory.gray.stream"),aligned(4)));

static void write32le(uint8_t *bytes,uint32_t value)
{
    for (uint32_t i=0;i<4u;++i) bytes[i]=(uint8_t)(value>>(i*8u));
}

/* Stock 0x31fc0 and 0x913c8. The device context already owns all 51 bytes
 * cleared before the battery update and the halfword at offset 42. */
void r1_battery_stats_clear(void)
{
    __aeabi_memclr((void *)(uintptr_t)r1_battery_device_context,51u);
}
uint32_t r1_battery_voltage_fresh_get(void)
{
    r1_battery_stats_clear();
    (void)r1_battery_runtime_update_service();
    return (uint32_t)r1_battery_device_context[42] |
           ((uint32_t)r1_battery_device_context[43]<<8);
}

/* Stock 0x815e4: send only the second through fourth 12-byte gray samples;
 * the fifth unregisters the listener and clears its counter. */
void r1_legacy_stream_sample_latch(uint32_t source,const void *payload,uint32_t length)
{
    (void)source;
    if (length<12u) return;
    const uint8_t *sample=payload;
    uint8_t count=(uint8_t)(r1_factory_mode_state.reserved[1]+1u);
    r1_factory_mode_state.reserved[1]=count;
    if (count>=5u) {
        r1_sensor_stream_unregister_by_name("gray",r1_factory_gray_stream_handle);
        r1_factory_gray_stream_handle=0u;
        r1_factory_mode_state.reserved[1]=0u;
        return;
    }
    uint8_t reply[36];
    __aeabi_memclr(reply,sizeof(reply));
    reply[1]=1u;
    reply[2]=0xf2u;
    reply[3]=0x12u;
    for (uint32_t i=0;i<12u;++i) reply[4u+i]=sample[i];
    if (count>1u) (void)r1_legacy_bounded_reply_send(reply,16u);
}

/* Stock 0x62c90: replace an earlier gray listener before registering the
 * five-sample factory stream. */
uint32_t r1_factory_stream_reregister(uint32_t handle,void *packet)
{
    (void)handle;(void)packet;
    uint32_t old=r1_factory_gray_stream_handle;
    if (old) {
        r1_sensor_stream_unregister_by_name("gray",old);
        r1_factory_gray_stream_handle=0u;
    }
    r1_factory_mode_state.reserved[1]=0u;
    r1_factory_gray_stream_handle=r1_sensor_stream_register_by_name(
        "gray","factory",(uintptr_t)r1_legacy_stream_sample_latch,1u,0u);
    return 0u;
}

static uint32_t reply_temperature_pair(void *packet)
{
    uint8_t *bytes=packet;
    r1_temperature_pair_read((volatile uint16_t *)(void *)(bytes+4));
    return r1_legacy_bounded_reply_send(packet,8u);
}
static uint32_t reply_payload_10(void *packet)
{
    r1_gxt310_id_pair_read((volatile uint8_t *)((uint8_t *)packet+4));
    return r1_legacy_bounded_reply_send(packet,10u);
}
static uint32_t reply_temperature_reduce(void *packet)
{
    uint8_t *bytes=packet;
    r1_temperature_pair_reduce((volatile void *)(bytes+4));
    return r1_legacy_bounded_reply_send(packet,5u+2u*bytes[4]);
}
static uint32_t reply_byte(void *packet,uint32_t value)
{
    ((uint8_t *)packet)[4]=(uint8_t)value;
    return r1_legacy_bounded_reply_send(packet,5u);
}
static uint32_t reply_yhm_status(void *packet)
{
    (void)r1_yhm_status_byte_get((volatile uint8_t *)((uint8_t *)packet+4));
    return r1_legacy_bounded_reply_send(packet,5u);
}
static uint32_t reply_temperature_word(void *packet)
{
    write32le((uint8_t *)packet+4,r1_gxt310_temp_average_read());
    return r1_legacy_bounded_reply_send(packet,8u);
}
static uint32_t reply_battery_voltage(void *packet)
{
    uint32_t value=r1_battery_voltage_fresh_get();
    ((uint8_t *)packet)[4]=(uint8_t)value;
    ((uint8_t *)packet)[5]=(uint8_t)(value>>8);
    return r1_legacy_bounded_reply_send(packet,6u);
}
static uint32_t delayed_reset(void *packet)
{
    (void)r1_legacy_bounded_reply_send(packet,4u);
    (void)osDelay(2000u);
    (void)r1_reset_trace_persist_tag_write(3u);
    r1_manager_system_reset();
}
static uint32_t ppg_mode(void *packet)
{
    const uint8_t *bytes=packet;
    if (bytes[4]==1u) r1_goodix_start_profile_4000();
    else if (bytes[5]==1u) r1_goodix_start_profile_2000();
    else r1_goodix_stop_stock_profiles();
    return r1_legacy_bounded_reply_send(packet,4u);
}
static uint32_t marked_ship(void *packet)
{
    (void)r1_legacy_bounded_reply_send(packet,4u);
    (void)osDelay(100u);
    (void)r1_kv_nv_r1_byte_set_c(0x5au);
    r1_sysctl_op_sequence_thunk();
    (void)osDelay(100u);
    return 0u;
}
static uint32_t ship(void *packet)
{
    (void)r1_legacy_bounded_reply_send(packet,4u);
    (void)osDelay(100u);
    r1_sysctl_op_sequence_thunk();
    (void)osDelay(100u);
    return 0u;
}

uint32_t r1_legacy_command_subdispatch(uint32_t handle,void *packet)
{
    uint8_t selector=((const uint8_t *)packet)[3];
    switch (selector) {
    case 0u: return reply_byte(packet,r1_goodix_identity_probe());
    case 1u: return reply_byte(packet,r1_motion_refresh_selection());
    case 2u: return reply_yhm_status(packet);
    case 3u: return reply_battery_voltage(packet);
    case 4u: return reply_temperature_word(packet);
    case 5u: return marked_ship(packet);
    case 6u: return ship(packet);
    case 8u: return ppg_mode(packet);
    case 9u: return delayed_reset(packet);
    case 18u: return r1_factory_stream_reregister(handle,packet);
    case 27u: return reply_byte(packet,r1_touch_chip_id_probe());
    case 31u: return reply_byte(packet,r1_nfc_chip_id_probe());
    case 44u: return reply_temperature_reduce(packet);
    case 48u: return reply_payload_10(packet);
    case 71u: return reply_temperature_pair(packet);
    default: return 0u;
    }
}
