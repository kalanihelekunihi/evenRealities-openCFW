/* Stock BLE peripheral watchdog 0x4d024. Its keep-connected byte is at
 * 0x200064b0; the periodic counter's cold RW byte is at 0x200064b1. */
#include <stdint.h>
#include "ble_advertising.h"
#include "ble_conn_state.h"
#include "cmsis_os2.h"
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern ble_advertising_t r1_ble_advertising_context_a;
extern uint32_t r1_gap_adv_addr_get(uint8_t);
extern void r1_adc_error(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_retained_log_printf_sink(const char *,...);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_connection_control_role_sync_thread_flags(uint32_t);
extern void r1_ble_flag_2000_callback(uint32_t);
volatile uint8_t r1_ble_peripheral_check_counter
 __attribute__((section(".r1.ble.peripheral_check_counter"),aligned(1)))=0;
volatile uint8_t r1_ble_keep_connected
 __attribute__((section(".r1.ble.keep_connected"),aligned(1)))=0;
/* Stock 0x4da1c stores the low byte of the keep-connected setting. */
void r1_ble_keep_connected_set(uint32_t enabled)
{r1_ble_keep_connected=(uint8_t)enabled;}
const char r1_ble_peripheral_count_ring[]="[RING]Periodic check: periph_link_cnt = %d";
const char r1_ble_peripheral_count_sdk[]="Periodic check: periph_link_cnt = %d";
const char r1_ble_peripheral_inconsistent_ring[]="[RING]system error: Both phone and glasses connected, reset system";
const char r1_ble_peripheral_inconsistent_sdk[]="system error: Both phone and glasses connected, reset system";
const char r1_ble_peripheral_restart_ring[]="[RING]advertising is started = %d";
const char r1_ble_peripheral_restart_sdk[]="advertising is started = %d";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void assertion_invalid_state(void)
{
    /* Native BLX uses an even stack address. Cortex-M rejects its clear Thumb
     * bit before executing any bytes. Keep that hardware fault class in C;
     * do not retain or execute the native stack opcode word. */
    volatile uint32_t stack_object=0;
    ((void (*)(void))(uintptr_t)&stack_object)();
}
void r1_peripheral_watchdog_plan_step(uint32_t argument)
{
    (void)argument;
    uint32_t count=ble_conn_state_peripheral_conn_count();
    uint8_t old=r1_ble_peripheral_check_counter;
    r1_ble_peripheral_check_counter=(uint8_t)(old+1u);
    if (old%60u==0) {
        if (ring_enabled()) r1_structured_log_format(0x0c400000,
             r1_ble_peripheral_count_ring,r1_ble_peripheral_count_ring,count);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0003,r1_ble_peripheral_count_sdk,count);
    }
    if (r1_ble_peripheral_check_counter==UINT8_MAX) r1_ble_peripheral_check_counter=0;
    if (count<2u) {
        if (r1_connection_field8!=UINT16_MAX && r1_connection_field10!=UINT16_MAX) {
            if (ring_enabled()) r1_structured_log_format(0x04000000,
                 r1_ble_peripheral_inconsistent_ring,r1_ble_peripheral_inconsistent_ring);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_0(0x001c0001,r1_ble_peripheral_inconsistent_sdk);
            (void)osDelay(500);
            (void)r1_retained_log_printf_sink("ASSERTION FAILED!");
            (void)r1_retained_log_printf_sink("File: %s","..\\..\\..\\platform\\ble\\app_ble_init.c");
            (void)r1_retained_log_printf_sink("Line: %d",1196);
            (void)r1_retained_log_printf_sink("Function: %s","app_ble_periodic_check_advertising");
            (void)r1_retained_log_printf_sink("Expression: %s","0");
            assertion_invalid_state();
            return;
        }
        volatile uint8_t *handle=&r1_ble_advertising_context_a.adv_handle;
        if (!r1_gap_adv_addr_get(*handle)) {
            (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
            uint32_t status=ble_advertising_start(&r1_ble_advertising_context_a,BLE_ADV_MODE_FAST);
            if (status) r1_adc_error(status);
            if (ring_enabled()) r1_structured_log_format(0x0c400000,
                 r1_ble_peripheral_restart_ring,r1_ble_peripheral_restart_ring,status);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_1(0x001c0003,r1_ble_peripheral_restart_sdk,status);
        }
    }
    r1_native_delayed_schedule(r1_ble_flag_2000_callback,0,0x2800);
}
