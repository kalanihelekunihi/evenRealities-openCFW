/* Exact-address ABI bindings to already selected mux bodies. The native
 * bank operations at these entries are the same functions as the source mux
 * on/off providers, so each binding preserves one full source-owned body. */
#include <stdint.h>
extern uint32_t audio_uart_mux_on0(uint32_t);  /* 0x4c3bfc */
extern uint32_t audio_uart_mux_on1(uint32_t);  /* 0x4c3c60 */
extern uint32_t audio_xtal_request(uint32_t);  /* 0x4c3d9e */
extern uint32_t audio_uart_mux_on3(uint32_t);  /* 0x4c3cd4 */
extern uint32_t audio_uart_mux_off0(uint32_t); /* 0x4c3c2e */
extern uint32_t audio_uart_mux_off1(uint32_t); /* 0x4c3ca2 */
extern uint32_t audio_uart_mux_off3(uint32_t); /* 0x4c3d28 */
extern uint32_t audio_uart_mux_off4(uint32_t); /* 0x4c4016 */
extern uint32_t audio_ble_vendor_irq_enable_bank2_4c3e9a(uint32_t); /* source 0x4c3e9a */
extern uint32_t audio_hfrc_request(uint32_t);  /* 0x4c3f2a */
extern uint32_t audio_hfrc2_request(uint32_t); /* 0x4c4086 */
extern uint32_t audio_hfrc2_release(uint32_t); /* 0x4c420c */
extern uint32_t audio_syspll_request(uint32_t);/* 0x4c427e */
extern uint32_t audio_syspll_release(uint32_t);/* 0x4c43ec */

uint32_t audio_ble_vendor_irq_disable_bank0_4c3bfc(uint32_t pin){return audio_uart_mux_on0(pin);}
uint32_t audio_ble_vendor_irq_disable_bank1_4c3c60(uint32_t pin){return audio_uart_mux_on1(pin);}
uint32_t audio_ble_vendor_irq_disable_bank2_4c3d9e(uint32_t pin){return audio_xtal_request(pin);}
uint32_t audio_ble_vendor_irq_disable_bank3_4c3cd4(uint32_t pin){return audio_uart_mux_on3(pin);}
uint32_t audio_ble_vendor_irq_disable_bank4_4c3f2a(uint32_t pin){return audio_hfrc_request(pin);}
uint32_t audio_ble_vendor_irq_disable_bank5_4c4086(uint32_t pin){return audio_hfrc2_request(pin);}
uint32_t audio_ble_vendor_irq_disable_bank6_4c427e(uint32_t pin){return audio_syspll_request(pin);}
uint32_t audio_ble_vendor_irq_enable_bank0_4c3c2e(uint32_t pin){return audio_uart_mux_off0(pin);}
uint32_t audio_ble_vendor_irq_enable_bank1_4c3ca2(uint32_t pin){return audio_uart_mux_off1(pin);}
uint32_t audio_ble_vendor_irq_enable_bank3_4c3d28(uint32_t pin){return audio_uart_mux_off3(pin);}
uint32_t audio_ble_vendor_irq_enable_bank4_4c4016(uint32_t pin){return audio_uart_mux_off4(pin);}
uint32_t audio_ble_vendor_irq_enable_bank5_4c420c(uint32_t pin){return audio_hfrc2_release(pin);}
uint32_t audio_ble_vendor_irq_enable_bank6_4c43ec(uint32_t pin){return audio_syspll_release(pin);}
uint32_t audio_uart_mux_on2(uint32_t pin){return audio_xtal_request(pin);}
uint32_t audio_uart_mux_off2(uint32_t pin){return audio_ble_vendor_irq_enable_bank2_4c3e9a(pin);}
uint32_t audio_uart_mux_on4(uint32_t pin){return audio_hfrc_request(pin);}
uint32_t audio_uart_mux_on5(uint32_t pin){return audio_hfrc2_request(pin);}
uint32_t audio_uart_mux_on6(uint32_t pin){return audio_syspll_request(pin);}
uint32_t audio_uart_mux_off5(uint32_t pin){return audio_hfrc2_release(pin);}
uint32_t audio_uart_mux_off6(uint32_t pin){return audio_syspll_release(pin);}
