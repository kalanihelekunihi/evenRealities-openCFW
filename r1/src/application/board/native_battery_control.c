#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[];
extern void *volatile r1_battery_thread_handle;
extern volatile uint32_t r1_shared_power_clients;
extern uint32_t osThreadFlagsSet(void *,uint32_t);
/* Native ABI transport boundary. The existing contextual YHM reconstruction
 * has a different device-pointer interface; transport/context binding is gated. */
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
uint32_t r1_yhm_shared_power_active(void)
{
    const uint8_t command=0xa8;return r1_yhm_register_write_native(2,1,&command);
}
uint32_t r1_yhm_shared_power_inactive(void)
{
    const uint8_t command=0x28;return r1_yhm_register_write_native(2,1,&command);
}
void r1_battery_charging_progress_reset(void)
{
    write32(r1_battery_device_context+52,0);write32(r1_battery_device_context+56,0);
    write32(r1_battery_device_context+60,0);write32(r1_battery_device_context+64,0);
}
uint32_t r1_battery_task_flags_set(uint32_t flags)
{ return osThreadFlagsSet(r1_battery_thread_handle,flags); }
void r1_shared_power_client_acquire(uint32_t client)
{
    if (client>=3) return;
    uint32_t bit=1u<<client,mask=r1_shared_power_clients;
    if (!(mask&bit)) {
        if (!mask) (void)r1_yhm_shared_power_active();
        r1_shared_power_clients=r1_shared_power_clients|bit;
    }
}
void r1_shared_power_client_release(uint32_t client)
{
    if (client>=3) return;
    uint32_t bit=1u<<client,mask=r1_shared_power_clients;
    if (mask&bit) {
        uint32_t remaining=mask&~bit;r1_shared_power_clients=remaining;
        if (!remaining) (void)r1_yhm_shared_power_inactive();
    }
}
