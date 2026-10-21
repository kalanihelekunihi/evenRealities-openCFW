/* Native receive dispatch0x826b4: checks buffer/length, then tail-forwards.
 * Callback return registers are observable; validation failures return the final
 * logging mode shift or SDK tail result rather than a synthesized status. */
#include <stdint.h>
extern volatile uintptr_t r1_protocol_receive_hook;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
typedef uint32_t (*receive_callback)(uint32_t,const void *,uint32_t,uintptr_t);
const char r1_protocol_receive_invalid_ring[] __attribute__((section(".r1.protocol_receive.invalid_ring")))="[RING]proto_ble_recv: invalid parameters";
const char r1_protocol_receive_invalid_sdk[] __attribute__((section(".r1.protocol_receive.invalid_sdk")))="proto_ble_recv: invalid parameters";
const char r1_protocol_receive_missing_ring[] __attribute__((section(".r1.protocol_receive.missing_ring")))="[RING]proto_ble_recv: recv callback not registered";
const char r1_protocol_receive_missing_sdk[] __attribute__((section(".r1.protocol_receive.missing_sdk")))="proto_ble_recv: recv callback not registered";
uint32_t r1_proto_ble_recv_validate(uint32_t handle,const void *packet,uint32_t length)
{
    const char *ring,*sdk;
    if(packet && length) {
        uintptr_t callback=r1_protocol_receive_hook;
        if(callback) return ((receive_callback)callback)(handle,packet,length,callback);
        ring=r1_protocol_receive_missing_ring;sdk=r1_protocol_receive_missing_sdk;
    } else {
        ring=r1_protocol_receive_invalid_ring;sdk=r1_protocol_receive_invalid_sdk;
    }
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,ring,ring);
    uint32_t mode=r1_structured_log_mode_get();
    if(mode&2u) return nrf_log_frontend_std_0(0x001c0001,sdk);
    return mode<<30;
}
