#include <stdint.h>
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_protocol_reset_workspace[640];
extern void *osMutexNew(const void *);
extern int32_t osMutexAcquire(void *,uint32_t),osMutexRelease(void *);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
void *volatile r1_ack_mutex __attribute__((section(".r1.ack.mutex"),aligned(4)))=0;
uint32_t r1_ack_mutex_control[20] __attribute__((section(".r1.ack.mutex.control"),aligned(4)))={0};
const char r1_ack_mutex_name[] __attribute__((section(".r1.ack.mutex.name")))="ack_mutex";
struct r1_ack_mutex_attributes {const char *name;uint32_t flags;void *memory;uint32_t size;};
const struct r1_ack_mutex_attributes r1_ack_mutex_attributes __attribute__((section(".r1.ack.mutex.attributes"),aligned(4)))={r1_ack_mutex_name,0,r1_ack_mutex_control,80};
_Static_assert(sizeof(struct r1_ack_mutex_attributes)==16,"native CMSIS mutex attributes");
__attribute__((noinline)) uint32_t r1_ack_table_lock(void)
{
 void *handle=r1_ack_mutex;
 if(!handle){handle=osMutexNew(&r1_ack_mutex_attributes);r1_ack_mutex=handle;}
 return (uint32_t)osMutexAcquire(handle,UINT32_MAX);
}
__attribute__((noinline)) uint32_t r1_ack_table_unlock(void)
{void *handle=r1_ack_mutex;return handle?(uint32_t)osMutexRelease(handle):0;}
__attribute__((noinline)) uintptr_t r1_packet_field12_get(const volatile uint8_t *packet)
{return (uint16_t)(read16(packet+8)-12u)?(uintptr_t)packet+12u:0;}
__attribute__((noinline)) uint32_t r1_ack_resolver(uint32_t first,uint32_t second,uint32_t third,uint32_t sequence)
{
 (void)r1_ack_table_lock();
 for(uint32_t i=0;i<32;i++){
  volatile uint8_t *record=r1_protocol_reset_workspace+20*i;
  if(!record[0]||record[1]!=first||record[2]!=second||record[3]!=third||read16(record+4)!=sequence)continue;
  uint32_t argument=read32(record+12),callback=read32(record+8);
  record[0]=0;write32(record+8,0);write32(record+12,0);
  uint32_t result=r1_ack_table_unlock();
  if(callback)return ((uint32_t (*)(uint32_t))(uintptr_t)callback)(argument);
  return result;
 }
 return r1_ack_table_unlock();
}
uint32_t r1_packet_ack_handler(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)handle;(void)scratch;(void)seed;
 const volatile uint8_t *payload=(const volatile uint8_t *)r1_packet_field12_get(packet);
 if(!payload)return 0;
 uint32_t sequence=read16(payload+4),third=payload[2],second=payload[1],first=payload[0];
 return r1_ack_resolver(first,second,third,sequence);
}
__attribute__((noinline,section(".r1.ack.restart.callback")))
void r1_delayed_restart_callback(uint32_t argument){(void)argument;}
void r1_delayed_event_restart(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)packet;(void)scratch;(void)seed;
 (void)r1_native_delayed_cancel(r1_delayed_restart_callback,0);
 r1_native_delayed_schedule(r1_delayed_restart_callback,handle,0x7800);
}
