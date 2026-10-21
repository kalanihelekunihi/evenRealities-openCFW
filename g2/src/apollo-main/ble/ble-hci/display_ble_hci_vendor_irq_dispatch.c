/* Native vendor IRQ route dispatch 0x4c44bc/0x4c4530.
 * Each of seven controller banks retains its genuine lower operation. */
#include <stdint.h>

extern uint32_t audio_ble_vendor_irq_disable_bank0_4c3bfc(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank1_4c3c60(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank2_4c3d9e(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank3_4c3cd4(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank4_4c3f2a(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank5_4c4086(uint32_t);
extern uint32_t audio_ble_vendor_irq_disable_bank6_4c427e(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank0_4c3c2e(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank1_4c3ca2(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank2_4c3e9a(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank3_4c3d28(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank4_4c4016(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank5_4c420c(uint32_t);
extern uint32_t audio_ble_vendor_irq_enable_bank6_4c43ec(uint32_t);

uint32_t audio_ble_vendor_irq_disable_4c44bc(uint32_t bank,uint32_t irq) {
    if((uint8_t)irq>=0x39u)return 6u;
    switch((uint8_t)bank) {
    case 0u:return audio_ble_vendor_irq_disable_bank0_4c3bfc((uint8_t)irq);
    case 1u:return audio_ble_vendor_irq_disable_bank1_4c3c60((uint8_t)irq);
    case 2u:return audio_ble_vendor_irq_disable_bank2_4c3d9e((uint8_t)irq);
    case 3u:return audio_ble_vendor_irq_disable_bank3_4c3cd4((uint8_t)irq);
    case 4u:return audio_ble_vendor_irq_disable_bank4_4c3f2a((uint8_t)irq);
    case 5u:return audio_ble_vendor_irq_disable_bank5_4c4086((uint8_t)irq);
    case 6u:return audio_ble_vendor_irq_disable_bank6_4c427e((uint8_t)irq);
    default:return 6u;
    }
}

uint32_t audio_ble_vendor_irq_enable_4c4530(uint32_t bank,uint32_t irq) {
    if((uint8_t)irq>=0x39u)return 6u;
    switch((uint8_t)bank) {
    case 0u:return audio_ble_vendor_irq_enable_bank0_4c3c2e((uint8_t)irq);
    case 1u:return audio_ble_vendor_irq_enable_bank1_4c3ca2((uint8_t)irq);
    case 2u:return audio_ble_vendor_irq_enable_bank2_4c3e9a((uint8_t)irq);
    case 3u:return audio_ble_vendor_irq_enable_bank3_4c3d28((uint8_t)irq);
    case 4u:return audio_ble_vendor_irq_enable_bank4_4c4016((uint8_t)irq);
    case 5u:return audio_ble_vendor_irq_enable_bank5_4c420c((uint8_t)irq);
    case 6u:return audio_ble_vendor_irq_enable_bank6_4c43ec((uint8_t)irq);
    default:return 6u;
    }
}
