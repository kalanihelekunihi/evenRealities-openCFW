/* Native BLE stack setup leaves 0x536324/48e/6cc/7ca/7f8/9ea and 0x4bae6c. */
#include <stdint.h>
extern uint8_t audio_ble_stack_state_20072cb8[]; /* live RAM 0x20072cb8 */
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live RAM 0x20073870 */
extern uint8_t audio_ble_hci_controller_state_20071478[]; /* live RAM 0x20071478 */
extern uint8_t audio_ble_hci_cmd_state_20073a90[]; /* live RAM 0x20073a90 */
extern uint8_t audio_ble_dm_config[]; /* selected live RAM 0x20000694 */
extern uint8_t audio_ble_dm_privacy_state[]; /* live RAM 0x20073b78 */
extern const uint8_t audio_ble_dm_stack_table_78a88c[]; /* ROM 0x78a88c */
extern void audio_ble_stack_callback_536234(void); /* Thumb 0x536235 */
extern void audio_ble_stack_callback_536470(void); /* Thumb 0x536471 */
extern void audio_ble_stack_callback_536620(void); /* Thumb 0x536621 */
extern void audio_ble_stack_callback_5366dc(void); /* Thumb 0x5366dd */
extern void audio_ble_hci_reset_state(void); /* 0x52ac02 */
extern void audio_ble_hci_controller_lower_530c00(void);
extern void audio_ble_dm_stack_state_init(void); /* 0x55ba70 */
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern uint8_t audio_ble_other_handler_id; /* RAM via 0x4bb3b8 */
extern void audio_ble_other_handler_start(void); /* 0x47a85c */
static void put(uint8_t *base,uint32_t offset,const void *p) {
    *(const void **)(void *)(base+offset)=p;
}
void audio_ble_stack_lower_5367ea(const void *p) { put(audio_ble_hci_stack_state_20073870,0x0cu,p); }
void audio_ble_dm_handler_lower_5367e4(const void *p) { put(audio_ble_hci_stack_state_20073870,8u,p); }
void audio_ble_stack_lower_536324(void) {
    for(uint32_t offset=0x20u;offset<=0x34u;offset+=4u)
        *(uint32_t *)(void *)(audio_ble_stack_state_20072cb8+offset)=0u;
    audio_ble_stack_state_20072cb8[0x38u]=0u;
    audio_ble_stack_lower_5367ea(audio_ble_stack_callback_536234);
}
void audio_ble_stack_lower_53648e(void) { put(audio_ble_stack_state_20072cb8,0x3cu,audio_ble_stack_callback_536470); }
void audio_ble_stack_lower_5366cc(void) { put(audio_ble_stack_state_20072cb8,0x40u,audio_ble_stack_callback_536620); }
void audio_ble_stack_lower_5367ca(void) { put(audio_ble_stack_state_20072cb8,0x44u,audio_ble_stack_callback_5366dc); }
void audio_ble_stack_lower_5367f8(uint8_t handler) {
    audio_ble_hci_stack_state_20073870[0x20u]=handler;
    *(uint32_t *)(void *)audio_ble_hci_stack_state_20073870=0u;
    *(uint32_t *)(void *)(audio_ble_hci_stack_state_20073870+4u)=0u;
    audio_ble_hci_reset_state();
}
void audio_ble_stack_lower_5369ea(void) {
    WsfTaskLock();
    put(audio_ble_dm_config,8u,audio_ble_dm_stack_table_78a88c);
    audio_ble_dm_stack_state_init();
    WsfTaskUnlock();
}
void audio_ble_stack_lower_4bae6c(uint8_t handler) {
    audio_ble_other_handler_id=handler;
    audio_ble_other_handler_start();
}
void audio_ble_dm_stack_state_init(void) { /* 0x55ba70 */
    uint8_t *rows=audio_ble_hci_stack_state_20073870+0x6cu;
    for(uint32_t i=0;i<2u;i++) {
        *(uint16_t *)(void *)(rows+0x10u+2u*i)=0x60u;
        *(uint16_t *)(void *)(rows+0x14u+2u*i)=0x30u;
    }
    audio_ble_dm_privacy_state[0x13u]=0u;
    rows[0x0cu]=audio_ble_dm_privacy_state[0x0cu];
    rows[0x18u]=0u;
    audio_ble_dm_privacy_state[0x0fu]=0u;
}
void audio_ble_hci_reset_state(void) { /* 0x52ac02 */
    uint8_t *base=audio_ble_hci_controller_state_20071478;
    *(uint32_t *)(void *)(base+0x70u)=0u;
    *(uint32_t *)(void *)(base+0x74u)=0u;
    for(uint32_t i=0;i<3u;i++)
        *(uint16_t *)(void *)(base+i*28u+0x10u)=0xffffu;
    for(uint32_t i=0;i<6u;i++)
        *(uint16_t *)(void *)(base+i*2u+0x54u)=0xffffu;
    *(uint16_t *)(void *)(base+0x7cu)=27u;
    base[0x80u]=14u;
    base[0x81u]=13u;
    *(uint32_t *)(void *)(base+0xa0u)=0u;
    audio_ble_hci_controller_lower_530c00();
}
void audio_ble_hci_controller_lower_530c00(void) { /* hciCoreInit */
    uint8_t *state=audio_ble_hci_cmd_state_20073a90;
    *(uint32_t *)(void *)(state+0x10u)=0u;
    *(uint32_t *)(void *)(state+0x14u)=0u;
    state[0x1au]=1u;
    state[0x0au]=1u;
    state[0x0cu]=audio_ble_hci_stack_state_20073870[0x20u];
}
