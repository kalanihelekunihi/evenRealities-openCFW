#include <stdint.h>
/* Product wrappers0x45c84/0x45d00 log only. Descriptor addresses are record IDs,
 * so keep distinct source strings and authenticated layout sections. */
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_service_init_ring[] __attribute__((section(".r1.thread_init_log.service_ring")))="[RING]thread_hardware_init";
const char r1_service_init_sdk[] __attribute__((section(".r1.thread_init_log.service_sdk")))="thread_hardware_init";
const char r1_storage_init_ring[] __attribute__((section(".r1.thread_init_log.storage_ring")))="[RING]thread_hardware_init";
const char r1_storage_init_sdk[] __attribute__((section(".r1.thread_init_log.storage_sdk")))="thread_hardware_init";
static void thread_init_log(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,sdk);
}
void r1_native_service_hardware_initialize(void) { thread_init_log(r1_service_init_ring,r1_service_init_sdk); }
void r1_native_storage_hardware_initialize(void) { thread_init_log(r1_storage_init_ring,r1_storage_init_sdk); }
