/* R1 application 0x4d654: connection-role policy and diagnostic sequence.
 * A conflicting live handle follows the stock assertion fault path. */
#include <stdint.h>
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_retained_log_printf_sink(const char *,...);
extern void r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
static const char initial_ring[]="[RING]app_ble_set_glasses_conn_handle: old=%d, new=%d, phone_conn_handle=%d";
static const char initial_sdk[]="app_ble_set_glasses_conn_handle: old=%d, new=%d, phone_conn_handle=%d";
static const char invalid_ring[]="[RING]Invalid conn_handle for glasses: 0x%x";
static const char invalid_sdk[]="Invalid conn_handle for glasses: 0x%x";
static const char conflict_ring[]="[RING]Glasses conn_handle (%d) conflicts with phone_conn_handle (%d)!";
static const char conflict_sdk[]="Glasses conn_handle (%d) conflicts with phone_conn_handle (%d)!";
static const char set_ring[]="[RING]glasses_conn_handle = %d";
static const char set_sdk[]="glasses_conn_handle = %d";
static const char ignored_ring[]="[RING]glasses_conn_handle already set to %d, ignoring new value %d";
static const char ignored_sdk[]="glasses_conn_handle already set to %d, ignoring new value %d";
static const char assertion[]="ASSERTION FAILED!";
static const char file_format[]="File: %s";
static const char file_name[]="..\\..\\..\\platform\\ble\\app_ble_init.c";
static const char line_format[]="Line: %d";
static const char function_format[]="Function: %s";
static const char function_name[]="app_ble_set_glasses_conn_handle";
static const char expression_format[]="Expression: %s";
static const char expression[]="0";
void r1_glasses_connection_role_assign(uint32_t handle)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t phone=r1_connection_field8;
        uint32_t old=r1_connection_field10;
        r1_structured_log_format(0x0cc00000,initial_ring,initial_ring,old,handle,phone);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t phone=r1_connection_field8;
        uint32_t old=r1_connection_field10;
        nrf_log_frontend_std_3(0x001c0003,initial_sdk,old,handle,phone);
    }
    if (handle==65535) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04400000,invalid_ring,invalid_ring,handle);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,invalid_sdk,handle);
        return;
    }
    if (r1_connection_field8==handle && r1_connection_field8!=65535) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04800000,conflict_ring,conflict_ring,handle,(uint32_t)r1_connection_field8);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x001c0001,conflict_sdk,handle,(uint32_t)r1_connection_field8);
        (void)osDelay(500);
        (void)r1_retained_log_printf_sink(assertion);
        (void)r1_retained_log_printf_sink(file_format,file_name);
        (void)r1_retained_log_printf_sink(line_format,1017);
        (void)r1_retained_log_printf_sink(function_format,function_name);
        (void)r1_retained_log_printf_sink(expression_format,expression);
        __builtin_trap();
    }
    if (r1_connection_field10==65535) {
        r1_connection_field10=(uint16_t)handle;
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x0c400000,set_ring,set_ring,(uint32_t)r1_connection_field10);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0003,set_sdk,(uint32_t)r1_connection_field10);
        r1_status_record_ring_publish(1,1,0,2);
        return;
    }
    if (r1_connection_field10==handle) return;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x08800000,ignored_ring,ignored_ring,(uint32_t)r1_connection_field10,handle);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0002,ignored_sdk,(uint32_t)r1_connection_field10,handle);
}
