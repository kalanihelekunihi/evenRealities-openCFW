#include <stdint.h>
#include "cmsis_os2.h"
#include "native_watchdog.h"

uint32_t r1_native_watchdog_port_start(uint32_t interval)
{
    if (!interval) return 0;
    r1_native_watchdog_hw_handle_init();r1_native_watchdog_hw_open_feed();return 1;
}
uint32_t r1_native_watchdog_port_stop(void)
{ r1_native_watchdog_hw_close();return 1; }
uint32_t r1_native_watchdog_port_sample(uint32_t operation,uint32_t *value)
{
    if (operation==0) r1_native_watchdog_hw_feed();
    else if (operation==1) *value=osKernelGetTickCount();
    else return 0;
    return 1;
}
struct r1_native_watchdog_port r1_native_watchdog_port_record
 __attribute__((section(".r1.watchdog.port"),aligned(4)))={
    r1_native_watchdog_port_start,r1_native_watchdog_port_stop,r1_native_watchdog_port_sample
};
struct r1_native_watchdog_port *r1_native_watchdog_port_get(void)
{ return &r1_native_watchdog_port_record; }
