/* Authenticated R1 module wrappers and shared command lookup. Native unsigned
 * index wrapping is preserved, including the below-minimum underflow path.
 * Symbolic command references are not implementations of their leaf handlers. */
#include <stdint.h>
#include "native_battery_memory.h"
struct r1_protocol_command { uint16_t key,reserved;uintptr_t callback; };
extern void r1_heart_rate_daily_handler(void);
extern void r1_heart_rate_point_handler(void);
extern void r1_heart_rate_measurement_plan(void);
extern void r1_spo2_daily_handler(void);
extern void r1_spo2_point_handler(void);
extern void r1_spo2_measurement_plan(void);
extern void r1_hrv_daily_handler(void);
extern void r1_hrv_point_handler(void);
extern void r1_health_history_noop_handler(void);
extern void r1_activity_daily_handler(void);
extern void r1_activity_refresh_handler(void);
extern void r1_sleep_daily_handler(void);
extern void r1_sleep_detail_plan(void);
extern void r1_health_report_setting_plan(void);
extern void r1_device_status_handler(void);
extern void r1_device_info_handler(void);
extern void r1_protocol_command_00084b24(void);
extern void r1_user_profile_handler(void);
extern void r1_protocol_command_000846dc(void);
extern void r1_touch_switch_handler_plan_decode(void);
extern void r1_pair_role_handler(void);
extern void r1_protocol_command_00083e2c(void);
extern void r1_connection_control_adv_start_handler_plan_decode(void);
extern void r1_protocol_command_00083e50(void);
extern void r1_protocol_command_000844ec(void);
extern void r1_health_settings_plan_command(void);
extern void r1_system_settings_plan_command(void);
extern void r1_device_serial_handler(void);
extern void r1_nv_recovery_command_handler_plan_decode(void);
extern void r1_protocol_command_000843c8(void);
extern void r1_packet_ack_handler(void);
extern void r1_delayed_event_restart(void);
extern void r1_protocol_command_000844b0(void);
extern void r1_protocol_command_00084860(void);
extern void r1_protocol_command_00084cc0(void);
const struct r1_protocol_command r1_protocol_health_commands[14] __attribute__((section(".r1.protocol_commands.health")))={
    {0x0101,0,(uintptr_t)&r1_heart_rate_daily_handler},
    {0x0102,0,(uintptr_t)&r1_heart_rate_point_handler},
    {0x0103,0,(uintptr_t)&r1_heart_rate_measurement_plan},
    {0x0201,0,(uintptr_t)&r1_spo2_daily_handler},
    {0x0202,0,(uintptr_t)&r1_spo2_point_handler},
    {0x0203,0,(uintptr_t)&r1_spo2_measurement_plan},
    {0x0401,0,(uintptr_t)&r1_hrv_daily_handler},
    {0x0402,0,(uintptr_t)&r1_hrv_point_handler},
    {0x0403,0,(uintptr_t)&r1_health_history_noop_handler},
    {0x0501,0,(uintptr_t)&r1_activity_daily_handler},
    {0x0502,0,(uintptr_t)&r1_activity_refresh_handler},
    {0x0601,0,(uintptr_t)&r1_sleep_daily_handler},
    {0x0602,0,(uintptr_t)&r1_sleep_detail_plan},
    {0x7f01,0,(uintptr_t)&r1_health_report_setting_plan},
};
const struct r1_protocol_command r1_protocol_system_commands[20] __attribute__((section(".r1.protocol_commands.system")))={
    {0x0001,0,(uintptr_t)&r1_device_status_handler},
    {0x0002,0,(uintptr_t)&r1_device_info_handler},
    {0x0003,0,(uintptr_t)&r1_protocol_command_00084b24},
    {0x0004,0,(uintptr_t)&r1_user_profile_handler},
    {0x0005,0,(uintptr_t)&r1_protocol_command_000846dc},
    {0x0007,0,(uintptr_t)&r1_touch_switch_handler_plan_decode},
    {0x0008,0,(uintptr_t)&r1_pair_role_handler},
    {0x0009,0,(uintptr_t)&r1_protocol_command_00083e2c},
    {0x000a,0,(uintptr_t)&r1_connection_control_adv_start_handler_plan_decode},
    {0x000b,0,(uintptr_t)&r1_protocol_command_00083e50},
    {0x000c,0,(uintptr_t)&r1_protocol_command_000844ec},
    {0x000e,0,(uintptr_t)&r1_health_settings_plan_command},
    {0x000f,0,(uintptr_t)&r1_system_settings_plan_command},
    {0x0010,0,(uintptr_t)&r1_device_serial_handler},
    {0x0011,0,(uintptr_t)&r1_nv_recovery_command_handler_plan_decode},
    {0x0012,0,(uintptr_t)&r1_protocol_command_000843c8},
    {0x007e,0,(uintptr_t)&r1_packet_ack_handler},
    {0x007f,0,(uintptr_t)&r1_delayed_event_restart},
    {0x0082,0,(uintptr_t)&r1_protocol_command_000844b0},
    {0x0083,0,(uintptr_t)&r1_protocol_command_00084860},
};
const struct r1_protocol_command r1_protocol_special_commands[1] __attribute__((section(".r1.protocol_commands.special")))={
    {0x0001,0,(uintptr_t)&r1_protocol_command_00084cc0},
};
uint32_t r1_health_registration_binary_search(uintptr_t table,uint32_t count,uint32_t command,uint32_t subcommand)
{
    uint32_t result=0,upper=count,index=command,lower=subcommand;
    if(table && count) {
        uint32_t key=(command<<8)|subcommand;
        upper=count-1u;lower=0;
        while(lower<=upper) {
            index=lower+((upper-lower)>>1);
            uint32_t address=(uint32_t)table+(index<<3);
            uint32_t observed=read16((const volatile uint8_t *)(uintptr_t)address);
            if(observed==key) { result=read32((const volatile uint8_t *)(uintptr_t)(address+4u));break; }
            if(observed<key) lower=index+1u;
            else upper=index-1u;
        }
    }
    register uint32_t out0 __asm__("r0")=result,out1 __asm__("r1")=upper;
    register uint32_t out2 __asm__("r2")=index,out3 __asm__("r3")=lower;
    __asm__ volatile("" : "+r"(out0), "+r"(out1), "+r"(out2), "+r"(out3));
    return out0;
}
typedef uint32_t (*command_callback)(uint32_t,const void *,uintptr_t,uint32_t);
#define MODULE_DISPATCH(name,table,count) \
uint32_t name(uint32_t handle,const void *packet) { \
    register uint32_t incoming2 __asm__("r2"),incoming3 __asm__("r3"); \
    __asm__ volatile("" : "+r"(incoming2), "+r"(incoming3) : : "memory"); \
    uint32_t result=handle,word2=incoming2,word3=incoming3;uintptr_t word1=(uintptr_t)packet; \
    if(packet) { \
        const volatile uint8_t *bytes=packet; \
        uint32_t command=bytes[6],subcommand=bytes[7]; \
        uintptr_t callback=r1_health_registration_binary_search((uintptr_t)table,count,command,subcommand); \
        register uint32_t native1 __asm__("r1"),native3 __asm__("r3"); \
        __asm__ volatile("" : "=r"(native1), "=r"(native3) : : "memory"); \
        word1=native1;word3=native3; \
        if(callback) return ((command_callback)callback)(handle,packet,callback,word3); \
        result=0;word2=0; \
    } \
    register uint32_t out0 __asm__("r0")=result,out2 __asm__("r2")=word2,out3 __asm__("r3")=word3; \
    register uintptr_t out1 __asm__("r1")=word1; \
    __asm__ volatile("" : "+r"(out0), "+r"(out1), "+r"(out2), "+r"(out3)); \
    return out0; \
}
MODULE_DISPATCH(r1_health_registration_dispatcher,r1_protocol_health_commands,14u)
MODULE_DISPATCH(r1_eus_system_dispatch_plan_build,r1_protocol_system_commands,20u)
MODULE_DISPATCH(r1_ble_event_dispatch,r1_protocol_special_commands,1u)
