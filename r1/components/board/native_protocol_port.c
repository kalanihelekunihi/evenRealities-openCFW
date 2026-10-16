/* R1 protocol port initialization and receive callback registration.
 * Presence/registration is not authentication. Ingress execution is a provider
 * seam; this unit owns only the native receive callback slot and reset order. */
#include <stdint.h>
extern volatile uintptr_t r1_protocol_send_hook;
volatile uintptr_t r1_protocol_receive_hook
    __attribute__((section(".r1.protocol.receive_hook"))) = 0;
extern uint32_t r1_protocol_send_callback_set(uintptr_t);
extern uint32_t r1_fragment_message(uint32_t,const void *,uint32_t);
extern void r1_eus_ingress_plan_decode(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_protocol_port_init_ring[] __attribute__((section(".r1.protocol_port.init_ring")))="[RING]proto_port_init: initialized successfully";
const char r1_protocol_port_init_sdk[] __attribute__((section(".r1.protocol_port.init_sdk")))="proto_port_init: initialized successfully";
const char r1_protocol_port_null_ring[] __attribute__((section(".r1.protocol_port.null_ring")))="[RING]proto_register_ble_recv_callback: callback is NULL";
const char r1_protocol_port_null_sdk[] __attribute__((section(".r1.protocol_port.null_sdk")))="proto_register_ble_recv_callback: callback is NULL";
const char r1_protocol_port_registered_ring[] __attribute__((section(".r1.protocol_port.registered_ring")))="[RING]proto_register_ble_recv_callback: registered successfully";
const char r1_protocol_port_registered_sdk[] __attribute__((section(".r1.protocol_port.registered_sdk")))="proto_register_ble_recv_callback: registered successfully";
uint32_t r1_proto_register_ble_recv_callback(uintptr_t callback)
{
    if(!callback) {
        if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04000000,r1_protocol_port_null_ring,r1_protocol_port_null_ring);
        if(r1_structured_log_mode_get()&2u)
            (void)nrf_log_frontend_std_0(0x001c0001,r1_protocol_port_null_sdk);
        return UINT32_MAX;
    }
    r1_protocol_receive_hook=callback;
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,r1_protocol_port_registered_ring,r1_protocol_port_registered_ring);
    if(r1_structured_log_mode_get()&2u)
        (void)nrf_log_frontend_std_0(0x001c0003,r1_protocol_port_registered_sdk);
    return 0;
}
uint32_t r1_proto_port_init(void)
{
    r1_protocol_send_hook=0;
    r1_protocol_receive_hook=0;
    (void)r1_protocol_send_callback_set((uintptr_t)&r1_fragment_message);
    (void)r1_proto_register_ble_recv_callback((uintptr_t)&r1_eus_ingress_plan_decode);
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,r1_protocol_port_init_ring,r1_protocol_port_init_ring);
    uint32_t mode=r1_structured_log_mode_get();
    if(mode&2u) return nrf_log_frontend_std_0(0x001c0003,r1_protocol_port_init_sdk);
    return mode<<30;
}
