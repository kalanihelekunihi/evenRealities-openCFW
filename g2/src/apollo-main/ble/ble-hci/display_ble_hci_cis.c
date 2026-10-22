/* Native CIS handle table 0x52ad9c/0x52adc2/0x52adec and wrappers
 * 0x52ae24/0x52ae2e. ROM slot 0x52ae20 -> live 0x200714cc. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
static uint8_t *cis_rows(void) {return audio_ble_hci_controller_state_20071478+0x54u;}
static uint16_t get16(const uint8_t *p) {return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));}
static void put16(uint8_t *p,uint16_t v) {p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}

/* Stock 0x52AD9C (hciCoreCisAlloc) */
void audio_ble_hci_cis_alloc(uint16_t handle) {
    uint8_t *p=cis_rows();
    for(uint32_t i=0u;i<6u;i++,p+=2u)if(get16(p)==0xffffu) {put16(p,handle);return;}
}
/* Stock 0x52ADC2 (hciCoreCisFree) */
void audio_ble_hci_cis_free(uint16_t handle) {
    uint8_t *p=cis_rows();
    for(uint32_t i=0u;i<6u;i++,p+=2u)if(get16(p)==handle) {put16(p,0xffffu);return;}
}
/* Stock 0x52ADEC (hciCoreCisByHandle) */
uint8_t *audio_ble_hci_cis_by_handle(uint16_t handle) {
    uint8_t *p=cis_rows();
    for(uint32_t i=0u;i<6u;i++,p+=2u)if(get16(p)==handle)return p;
    return 0;
}
/* Stock 0x52AE24 (hciCoreCisOpen) */
__attribute__((naked)) uint32_t audio_ble_hci_cis_open(uint16_t handle) {
    __asm volatile("push {r7, lr}\n\tbl audio_ble_hci_cis_alloc\n\tpop {r7, lr}\n\tmov r0, r7\n\tbx lr");
}
/* Stock 0x52AE2E (hciCoreCisClose) */
__attribute__((naked)) uint32_t audio_ble_hci_cis_close(uint16_t handle) {
    __asm volatile("push {r7, lr}\n\tbl audio_ble_hci_cis_free\n\tpop {r7, lr}\n\tmov r0, r7\n\tbx lr");
}
