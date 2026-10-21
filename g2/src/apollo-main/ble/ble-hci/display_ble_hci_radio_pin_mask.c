/* Native 0x4810b0 GPIO interrupt mask operation. ROM literal slots
 * 0x481768..9c point at Apollo GPIO registers 0x40010530..0x40010600. */
#include <stdint.h>
extern uint32_t g2_power_critical_save(void); /* native 0x473940 */
extern void g2_power_critical_restore(uint32_t); /* architectural MSR PRIMASK */

uint32_t audio_ble_hci_radio_pin_mask_4810b0(uint32_t bank,uint32_t operation,
                                              uint32_t *pins) {
    if(pins==0||(operation&0xffu)>=4u)return 6u;
    uint32_t op=operation&0xffu;
    uint32_t group=0u,mask=0u;
    if(op<2u) {
        uint32_t pin=pins[0];
        if(pin>0xdfu)return 5u;
        group=pin>>5;
        mask=1u<<(pin&31u);
    }
    uint32_t saved=g2_power_critical_save();
    /* Each GPIO bank's seven mask registers are 0x10 bytes apart. */
    volatile uint32_t *a=(volatile uint32_t *)(uintptr_t)0x40010530u;
    volatile uint32_t *b=(volatile uint32_t *)(uintptr_t)0x400105a0u;
    if(op==0u) {
        volatile uint32_t *first=((bank&0xffu)==1u)?b:a;
        first[group*4u]&=~mask;
        if((bank&0xffu)==2u)b[group*4u]&=~mask;
    } else if(op==1u) {
        volatile uint32_t *first=((bank&0xffu)==1u)?b:a;
        first[group*4u]|=mask;
        if((bank&0xffu)==2u)b[group*4u]|=mask;
    } else if(op==2u) {
        if((bank&0xffu)!=1u)for(uint32_t i=0;i<7u;i++)a[i*4u]&=~pins[i];
        if((bank&0xffu)!=0u)for(uint32_t i=0;i<7u;i++)b[i*4u]&=~pins[i];
    } else {
        if((bank&0xffu)!=1u)for(uint32_t i=0;i<7u;i++)a[i*4u]|=pins[i];
        if((bank&0xffu)!=0u)for(uint32_t i=0;i<7u;i++)b[i*4u]|=pins[i];
    }
    g2_power_critical_restore(saved);
    return 0u;
}
