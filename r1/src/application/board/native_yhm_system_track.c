/* PMIC system-tracking set/clear operations use ordinary C status ABIs.
 * Read status is ignored; logging mode is sampled live at each branch. */
#include <stdint.h>
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_yhm_system_track_ring[] __attribute__((section(".r1.yhm_track.ring")))="[RING]YHM2710_set_sys_track txdata = 0x%02x";
const char r1_yhm_system_track_sdk[] __attribute__((section(".r1.yhm_track.sdk")))="YHM2710_set_sys_track txdata = 0x%02x";
__attribute__((noinline)) uint32_t r1_yhm_system_track_native(void)
{
    volatile struct { uint32_t tx,rx; } frame={0,0};
    ((volatile uint8_t *)&frame.rx)[0]=0;
    (void)r1_yhm_register_read_native(1,1,(uint8_t *)(uintptr_t)&frame.rx);
    ((volatile uint8_t *)&frame.tx)[0]=(uint8_t)(((volatile uint8_t *)&frame.rx)[0]|2u);
    
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        r1_structured_log_format(0x0c400000,r1_yhm_system_track_ring,r1_yhm_system_track_ring,(uint32_t)((volatile uint8_t *)&frame.tx)[0]);
    }
    
    if (r1_structured_log_mode_get()&2u) {
        nrf_log_frontend_std_1(0x001c0003,r1_yhm_system_track_sdk,((volatile uint8_t *)&frame.tx)[0]);
    }
    uint32_t status=r1_yhm_register_write_native(1,1,(const uint8_t *)(uintptr_t)&frame.tx);
    return status;
}
uint32_t r1_native_charger_initialize(void) { return r1_yhm_system_track_native(); }

/* Stock 0x3543c and its 0x5074c tail: clear bit 1 with the same exposed
 * partial-word and logging contracts as the setter above. */
const char r1_yhm_system_track_clear_ring[] __attribute__((section(".r1.yhm_track.ring")))="[RING]YHM2710_reset_sys_track txdata = 0x%02x";
const char r1_yhm_system_track_clear_sdk[] __attribute__((section(".r1.yhm_track.sdk")))="YHM2710_reset_sys_track txdata = 0x%02x";
__attribute__((noinline)) uint32_t r1_yhm_system_track_clear_native(void)
{
    volatile struct { uint32_t tx,rx; } frame={0,0};
    ((volatile uint8_t *)&frame.rx)[0]=0;
    (void)r1_yhm_register_read_native(1,1,(uint8_t *)(uintptr_t)&frame.rx);
    ((volatile uint8_t *)&frame.tx)[0]=(uint8_t)(((volatile uint8_t *)&frame.rx)[0]&~2u);
    
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        r1_structured_log_format(0x0c400000,r1_yhm_system_track_clear_ring,r1_yhm_system_track_clear_ring,(uint32_t)((volatile uint8_t *)&frame.tx)[0]);
    }
    
    if (r1_structured_log_mode_get()&2u) {
        nrf_log_frontend_std_1(0x001c0003,r1_yhm_system_track_clear_sdk,((volatile uint8_t *)&frame.tx)[0]);
    }
    uint32_t status=r1_yhm_register_write_native(1,1,(const uint8_t *)(uintptr_t)&frame.tx);
    return status;
}
uint32_t r1_native_charger_tracking_clear(void) { return r1_yhm_system_track_clear_native(); }


