/* Native Cordio DM/L2CAP/SMP/HCI registration bodies selected by
 * _bleExactleStackInit. All callback targets come from native literals. */
#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18u]; /* RAM 0x20073b78 */
uint8_t audio_ble_l2c_slave_state[0x18u]; /* RAM 0x20073bd8, init writes through +0x16 */
uint8_t audio_ble_smp_handler_state[0xfcu]; /* RAM 0x20070aec; SC writes through +0xf8 */
uint8_t audio_ble_hci_state[0x80u]; /* RAM 0x20071478 */
extern void audio_ble_dm_handler_lower_5367e4(void (*)(void));
extern void audio_ble_dm_handler_4d299c(void); /* stock callback 0x4d299d */
extern void SmpDbInit(void);
extern void L2cRegister(uint8_t,void (*)(void),void (*)(void));
extern void DmConnRegister(uint8_t,void (*)(void));
extern void audio_ble_smp_l2c_data_callback_537278(void);
extern void audio_ble_smp_l2c_control_callback_537444(void);
extern void audio_ble_smp_dm_conn_callback_537502(void);

void DmHandlerInit(uint8_t handler) { /* 0x4d2a46 */
    audio_ble_dm_handler_state[0x0cu]=handler;
    audio_ble_dm_handler_state[0x16u]=0u;
    audio_ble_dm_handler_state[0x10u]=0u;
    audio_ble_dm_handler_lower_5367e4(audio_ble_dm_handler_4d299c);
}
void L2cSlaveHandlerInit(uint8_t handler) { /* 0x536f6a */
    audio_ble_l2c_slave_state[0x0au]=1u;
    audio_ble_l2c_slave_state[0x0cu]=handler;
    audio_ble_l2c_slave_state[0x10u]=handler;
}
void SmpHandlerInit(uint8_t handler) { /* 0x537cb2 */
    audio_ble_smp_handler_state[0xecu]=handler;
    SmpDbInit();
    for(uint32_t i=0;i<3u;i++) {
        uint8_t *row=audio_ble_smp_handler_state+i*0x4cu;
        row[0x0cu]=handler;
        *(uint16_t *)(void *)(row+8u)=(uint16_t)(i+1u);
        row[0x1cu]=handler;
        *(uint16_t *)(void *)(row+0x18u)=(uint16_t)(i+1u);
    }
    L2cRegister(6u,audio_ble_smp_l2c_data_callback_537278,
                audio_ble_smp_l2c_control_callback_537444);
    DmConnRegister(1u,audio_ble_smp_dm_conn_callback_537502);
}
void HciSetMaxRxAclLen(uint16_t length) { /* 0x52acce */
    *(uint16_t *)(void *)(audio_ble_hci_state+0x7cu)=length;
}
