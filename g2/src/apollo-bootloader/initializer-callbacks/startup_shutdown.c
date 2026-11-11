/* SPDX-License-Identifier: MIT. Independent reconstruction of locked f89a4c46
 * Thumb bodies423d20..423d9a,423da0..423dce,423dd0..423e0c,
 * and422468..422574. Register names deliberately do not imply hardware drain. */
#include "startup_shutdown.h"
#include "../platform-control/am_hal_pwrctrl_api.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t am_hal_interrupt_master_disable(void);
extern uint32_t am_hal_delay_us_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern void opencfw_hal_delay_us(uint32_t);
static inline void restore(uint32_t saved){__asm__ volatile("msr primask,%0"::"r"(saved):"memory");}
/* Stock 0x423DA0 (stage_one_wait_index; am_hal_itm_stimulus_not_busy) */
NI uint32_t opencfw_boot_shutdown_wait_slot(uint32_t slot){
 return am_hal_delay_us_status_change(1000,(volatile uint32_t *)(uintptr_t)(0xe0000000u+(slot<<2)),3,1)==0;
}
/* Stock 0x423DC4 (stage_one_wait_zero; am_hal_itm_print_not_busy) */
NI uint32_t opencfw_boot_shutdown_wait_zero(void){return opencfw_boot_shutdown_wait_slot(0);}
/* Stock 0x423D7A (stage_one_wait_reg80; am_hal_itm_not_busy) */
NI uint32_t opencfw_boot_shutdown_wait_clear(void){
 return am_hal_delay_us_status_change(1000,(volatile uint32_t *)(uintptr_t)0xe0000e80u,0x800000,0)==0;
}
/* Stock 0x423D58 (stage_one_status; am_hal_itm_tpiu_pipeline_flush) */
NI uint32_t opencfw_boot_shutdown_prepare(void){
 if(!opencfw_boot_shutdown_wait_zero() || !opencfw_boot_shutdown_wait_clear())return 4;
 opencfw_hal_delay_us(500);return 0;
}
/* AmbiqSuite am_hal_debug.c trace-enable count; stock cell 0x200271a3 (pinned in
 * link/g2-apollo-bootloader.ld), also read by upstream am_hal_pwrctrl_low_power_init. */
uint8_t g_ui8TRCENAcount;
NI uint32_t opencfw_boot_shutdown_debug_release(void){
 uint32_t saved=am_hal_interrupt_master_disable(),status;
 if(g_ui8TRCENAcount)g_ui8TRCENAcount--;
 if(g_ui8TRCENAcount)status=3;
 else {W(0xe000edfcu)&=~0x1000000u;status=am_hal_delay_us_status_change(10,(volatile uint32_t *)(uintptr_t)0xe000edfcu,0x1000000,0);}
 restore(saved);return status;
}
/* AmbiqSuite am_hal_debug.c name (stock 0x42252e). */
uint32_t am_hal_debug_trace_disable(void) __attribute__((alias("opencfw_boot_shutdown_debug_release")));
NI uint32_t opencfw_boot_shutdown_resource(uint32_t enable){
 uint32_t saved=am_hal_interrupt_master_disable(),status=0;
 if((uint8_t)enable){
  B(0x200271a2)++;
  if(!B(0x200271a4)){
   uint8_t active;B(0x200271a4)=1;
   (void)am_hal_pwrctrl_periph_enabled(28,(bool *)&active);
   if(active)B(0x200271a4)|=2;
   else (void)am_hal_pwrctrl_periph_enable(28);
  }
 }else{
  if(B(0x200271a2))B(0x200271a2)--;
  if(B(0x200271a2))status=3;
  else {if(B(0x200271a4)==1)(void)am_hal_pwrctrl_periph_disable(28);B(0x200271a4)=0;}
 }
 restore(saved);return status;
}
/* Stock 0x422468 (debug_disable; am_hal_debug_disable) */
NI uint32_t opencfw_boot_shutdown_clock_release(void){
 uint32_t saved=am_hal_interrupt_master_disable();
 if(B(0x200271a1))B(0x200271a1)--;
 if(!B(0x200271a1)){W(0x40020250u)&=~1u;W(0x40020250u)&=~14u;}
 /* Stock discards even the outstanding-reference status3 and debug result. */
 (void)opencfw_boot_shutdown_debug_release();
 uint32_t status=opencfw_boot_shutdown_resource(0);restore(saved);return status;
}
/* Stock 0x423D20 (stage_one_entry; am_hal_itm_disable) */
NI uint32_t opencfw_boot_startup_shutdown_first(void){
 /* Stock ignores the preparatory timeout, continues register writes. */
 (void)opencfw_boot_shutdown_prepare();
 W(0xe0000e80u)&=~16u;W(0xe0000e80u)&=~1u;
 uint32_t status=am_hal_delay_us_status_change(1000,(volatile uint32_t *)(uintptr_t)0xe0000e80u,0,0);
 if(!status){status=opencfw_boot_shutdown_clock_release();if(status==3)status=0;}
 return status;
}
/* Stock 0x423DD0 (stage_two_status; am_hal_tpiu_disable) */
NI uint32_t opencfw_boot_startup_shutdown_second(void){
 uint32_t saved=am_hal_interrupt_master_disable(),status;
 if(B(0x200271c3))B(0x200271c3)--;
 if(B(0x200271c3))status=3;
 else {B(0x200271c2)=0;status=opencfw_boot_shutdown_clock_release();if(status==3)status=0;}
 restore(saved);return status;
}
