/* SPDX-License-Identifier: MIT */
#ifndef TOUCH_ACTIVE_SCAN_CONTEXT_H
#define TOUCH_ACTIVE_SCAN_CONTEXT_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
 const void *ptrEltdConfig;
 const void *ptrRxConfig;
 const void *ptrTxConfig;
 void *ptrSnsContext;
 uint16_t currentChannelSlotIndex;
 uint16_t sensorIndex;
 uint8_t widgetIndex;
 uint8_t currentSenseMethod;
 uint8_t connectedSnsState;
} touch_active_scan_sns_v6_lp;
_Static_assert(sizeof(touch_active_scan_sns_v6_lp)==24u,"active-scan ABI");
_Static_assert(offsetof(touch_active_scan_sns_v6_lp,currentChannelSlotIndex)==16u,"active-scan slot ABI");
_Static_assert(offsetof(touch_active_scan_sns_v6_lp,connectedSnsState)==22u,"active-scan state ABI");
extern touch_active_scan_sns_v6_lp touch_generated_active_scan_sns;
#endif
