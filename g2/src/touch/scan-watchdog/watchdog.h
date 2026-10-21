#ifndef TOUCH_SCAN_WATCHDOG_OFFLINE_H
#define TOUCH_SCAN_WATCHDOG_OFFLINE_H
#include <stdint.h>
uint32_t touch_scan_watchdog(uint32_t id,uint32_t slot,const uint8_t *context);
uint32_t touch_scan_wait(uint32_t watchdog,const uint8_t *context);
#endif
