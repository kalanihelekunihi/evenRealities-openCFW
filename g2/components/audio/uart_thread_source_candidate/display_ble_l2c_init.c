/* Native Cordio L2CAP init/register 0x530b34/5e, 0x536e78, 0x537200.
 * The shared L2CAP state is live BSS at stock RAM 0x200737d8. */
#include <stdint.h>
uint8_t audio_ble_l2c_state[0x30u];
extern uint8_t audio_ble_l2c_slave_state[]; /* RAM 0x20073bd8 */
extern void audio_ble_l2c_default_data_530538(void);
extern void audio_ble_l2c_rx_signaling_53076e(void);
extern void audio_ble_l2c_default_control_53076c(void);
extern void audio_ble_l2c_default_cid_530640(void);
extern void audio_ble_l2c_hci_acl_5308e6(void);
extern void audio_ble_l2c_hci_flow_530aa4(void);
extern void audio_ble_l2c_slave_rx_536c5c(void);
extern void audio_ble_l2c_master_rx_536fbc(void);
extern void audio_ble_l2c_hci_register(void (*)(void),void (*)(void)); /* 0x5367f0 */
static void put(uint32_t offset,const void *p) {
    *(const void **)(void *)(audio_ble_l2c_state+offset)=p;
}
void L2cInit(void) {
    put(0u,audio_ble_l2c_default_data_530538);
    put(4u,audio_ble_l2c_default_data_530538);
    put(8u,audio_ble_l2c_rx_signaling_53076e);
    put(12u,audio_ble_l2c_default_control_53076c);
    put(16u,audio_ble_l2c_default_control_53076c);
    put(20u,audio_ble_l2c_default_control_53076c);
    put(32u,audio_ble_l2c_default_cid_530640);
    audio_ble_l2c_state[36u]=1u;
    audio_ble_l2c_hci_register(audio_ble_l2c_hci_acl_5308e6,
                               audio_ble_l2c_hci_flow_530aa4);
}
void L2cRegister(uint16_t cid,void (*data)(void),void (*control)(void)) {
    if(cid==4u) {put(0u,data);put(12u,control);}
    else {put(4u,data);put(16u,control);}
}
void L2cSlaveInit(void) {
    put(28u,audio_ble_l2c_slave_rx_536c5c);
    audio_ble_l2c_slave_state[0x14u]=0u;
    audio_ble_l2c_slave_state[0x15u]=0u;
    audio_ble_l2c_slave_state[0x16u]=0u;
}
void L2cMasterInit(void) {put(24u,audio_ble_l2c_master_rx_536fbc);}
