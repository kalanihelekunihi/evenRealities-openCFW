/* Stock 0x731a0: bind the port and register the seven live NV classes. */
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
extern void r1_kv_port_bind(struct r1_kv_port_view *volatile *);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
volatile uint16_t r1_nv_registered_class_count
 __attribute__((section(".r1.nv.registered.count"),aligned(2)))=0;
void r1_storage_manager_initialize_731a0(void)
{
 r1_kv_port_bind(&r1_kv_port);
 uint32_t (*initialize)(void)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port);
 (void)initialize();
 r1_nv_registered_class_count=0;
 volatile uint32_t base=0;
 uint32_t (*control)(uint32_t,uint32_t *)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port+24);
 (void)control(3,(uint32_t *)&base);
 for(uint32_t i=0;i<R1_NV_HANDLE_COUNT;i++){
  volatile uint8_t *node=*r1_nv_handle_owners[i];
  if(read16(node+20)>=232u)r1_bae8_rx_allocation_fault();
  uint16_t count=(uint16_t)(r1_nv_registered_class_count+1u);
  r1_nv_registered_class_count=count;
  if(count>=8u)r1_bae8_rx_allocation_fault();
  node[11]=0;
  uint32_t hash=r1_stock_hash131((const uint8_t *)(uintptr_t)(node+4),8);
  write32(node,hash);
  write32(node+12,base);
 }
 (void)r1_nv_store_bootstrap_73220();
}
