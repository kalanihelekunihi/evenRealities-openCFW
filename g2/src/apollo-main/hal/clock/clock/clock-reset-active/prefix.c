#include "prefix.h"
#include "recovery.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern void stock_trace_disable(void),stock_info_populate(void);
extern uint32_t stock_disable(uint32_t),stock_enable(uint32_t);
extern uint32_t stock_peripheral_enabled(uint32_t,uint8_t*);
extern uint32_t stock_cpdlp_config(uint32_t);
extern uint32_t stock_revision(uint32_t*);
extern uint32_t stock_info_read(uint32_t,uint32_t,uint32_t,uint32_t*);
extern uint32_t stock_register_callbacks(void),stock_mcu_memory_config(uint32_t*),stock_sram_config(const void*);
extern uint32_t pcm_common_capture_ton_block(void),pcm_lp_initialize_dispatch(void);
uint32_t pcm_common_low_power_initialize(uint32_t incoming_r5){
 uint32_t version=0;uint8_t enabled=0;
 if(W(0x4000885c)&2)W(0x4000885c)&=~4u;
 if(!B(0x20074f5e)){
  stock_trace_disable();(void)stock_disable(28);
  W(0x40020250)&=~1u;W(0x40020250)&=~14u;
 }
 (void)stock_cpdlp_config(W(0x78ee50));W(0x4002021c)|=1;
 if(W(0x400201bc)&8){(void)stock_peripheral_enabled(29,&enabled);if(!enabled)(void)stock_enable(29);}
 (void)stock_revision(&version);stock_info_populate();
 if(W(0x20071948)!=0x1f01600d){
  uint32_t status=stock_info_read(1,0x210,1,(uint32_t*)0x2007197c);if(status)return status;
  status=stock_info_read(1,0x245,1,(uint32_t*)0x2007198c);if(status)return status;
 }
 (void)stock_register_callbacks();(void)stock_disable(23);(void)stock_disable(29);
 if((W(0x4002000c)&255)>=0x22)B(0x200001ec)=1;
 (void)stock_mcu_memory_config((uint32_t*)0x200001ec);(void)stock_sram_config((const void*)0x78c984);
 W(0x40004044)=((W(0x40004044)|0xf80000u)|0x3bfc0u)&~0x4000u;
 W(0x40004120)=0;W(0x40020448)=(W(0x40020448)&~0xff00u)|0x400;
 uint32_t clock_r5=B(0x20074f63)?incoming_r5:0x20074284;
 (void)pcm_common_capture_ton_block();(void)pcm_lp_initialize_dispatch();clock_reset_recover(clock_r5);
 if((W(0x4002000c)&255)>=0x22)W(0x400211c8)|=6;
 return 0;
}
