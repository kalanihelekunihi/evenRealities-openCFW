#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_phone_cmd_send_op1(const void *,uint32_t,uint32_t);
const char r1_battery_protocol_ring[] __attribute__((section(".r1.battery_protocol.ring")))="[RING]proto report battery status, percent: %d, charge status: %d";
const char r1_battery_protocol_sdk[] __attribute__((section(".r1.battery_protocol.sdk")))="proto report battery status, percent: %d, charge status: %d";
/* Stock packet layout and dispatch behavior with the ordinary C result ABI.
 * Caller-clobbered scratch register restoration is intentionally retired. */
__attribute__((noinline)) uint32_t r1_proto_report_battery_status(uint32_t level,uint32_t state)
{
    volatile uint32_t packet[2]={(uint8_t)level|((state ? 1u:2u)<<8),0};
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t charge=((const volatile uint8_t *)packet)[1];
        (void)r1_structured_log_format(0x0c800000,r1_battery_protocol_ring,r1_battery_protocol_ring,level,charge);
    }
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,r1_battery_protocol_sdk,level,((const volatile uint8_t *)packet)[1]);
    uint32_t result=r1_phone_cmd_send_op1((const void *)packet,1,0);
    return result;
}
