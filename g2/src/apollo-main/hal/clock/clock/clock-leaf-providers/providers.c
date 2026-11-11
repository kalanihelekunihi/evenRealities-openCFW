#include "providers.h"
#include "../clock-manager-ownership/ownership.h"
#include "../../../gpio/gpio-providers/gpio.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");
#define W(a) (*(volatile uint32_t *)(a))
extern uint32_t stock_save_irq(void),stock_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void stock_delay(uint32_t);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
uint32_t audio_ext_request(uint32_t u){u=(uint8_t)u;if(!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u)))return 7;if(audio_clock_user(3,u))return 0;uint32_t m=stock_save_irq();audio_gpio_pin_set(15,10);audio_clock_set(3,u,1);restore(m);return 0;}
uint32_t audio_ext_release(uint32_t u){u=(uint8_t)u;if(!audio_clock_user(3,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(3,u,0);if(!audio_clock_any(3))audio_gpio_pin_set(15,3);restore(m);return 0;}
/* am_hal_pwrctrl_syspll_enable/disable/enabled (stock 0x480058/0x48009e/0x4800e4)
 * formerly here now come from AmbiqSuite 5.1.0 hal/am_hal_pwrctrl.c. */
/* The eight am_hal_clkgen leaves formerly here (stock 0x4D38EA..0x4D39E4)
 * now come from AmbiqSuite 5.1.0 hal/mcu/am_hal_clkgen.c; their old names
 * are bound to the upstream names by the payload defsym map. */
