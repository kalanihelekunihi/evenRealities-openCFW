#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_phone_cmd_send_op1(const void *,uint32_t,uint32_t);
const char r1_battery_protocol_ring[] __attribute__((section(".r1.battery_protocol.ring")))="[RING]proto report battery status, percent: %d, charge status: %d";
const char r1_battery_protocol_sdk[] __attribute__((section(".r1.battery_protocol.sdk")))="proto report battery status, percent: %d, charge status: %d";
/* Native0x8345c saves incoming r1 as its log argument word, zeroes the two
 * packet words, then restores all three words to r1/r2/r3 after dispatch. */
__attribute__((noinline)) uint32_t r1_proto_report_battery_status(uint32_t level,uint32_t state)
{
    volatile uint32_t saved1=state;
    volatile uint32_t packet[2]={(uint8_t)level|((state ? 1u:2u)<<8),0};
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t charge=((const volatile uint8_t *)packet)[1];saved1=charge;
        (void)r1_structured_log_format(0x0c800000,r1_battery_protocol_ring,r1_battery_protocol_ring,level,charge);
    }
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,r1_battery_protocol_sdk,level,((const volatile uint8_t *)packet)[1]);
    uint32_t result=r1_phone_cmd_send_op1((const void *)packet,1,0);
    uint32_t restored1=saved1,restored2=packet[0],restored3=packet[1];
    __asm__ volatile("mov r1, %0\nmov r2, %1\nmov r3, %2" : : "r"(restored1),"r"(restored2),"r"(restored3) : "r1","r2","r3");
    return result;
}
