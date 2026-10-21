/* Native l2cHciFlowCback 0x530aa4. Its callback ABI supplies handle in R0
 * and packet count in R1; original R3 contributes the fourth event byte.
 * The entry branch captures the actual incoming register without creating an
 * indeterminate C local or synthesizing an ambient value. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t DmConnIdByHandle(uint16_t); /* selected 0x4b6e96 */
extern uint8_t audio_ble_l2c_state[0x30]; /* source-owned RAM 0x200737d8 */
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
__attribute__((used,noinline))
uint32_t audio_ble_l2c_hci_flow_impl(uint32_t handle,uint32_t count,
                                     uint32_t unused,uint32_t incoming_r3) {
    (void)unused;
    uint16_t conn=DmConnIdByHandle((uint16_t)handle);
    uint32_t event=(incoming_r3&0xffff0000u)|conn;
    if(conn==0u) return event;
    for(uint32_t i=0;i<3u;i++) {
        event=(event&0xff00ffffu)|((count&0xffu)<<16);
        void (*callback)(uint32_t *)=
            (void (*)(uint32_t *))(uintptr_t)get32(audio_ble_l2c_state+12u+4u*i);
        callback(&event);
    }
    return event;
}
__attribute__((naked)) uint32_t audio_ble_l2c_hci_flow_530aa4(void) {
    __asm__ volatile("b.w audio_ble_l2c_hci_flow_impl");
}
