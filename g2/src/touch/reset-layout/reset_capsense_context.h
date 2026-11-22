/* SPDX-License-Identifier: MIT
 * Recovered CapSense v6 LP top-level context, reset-copied to 0x200004ec.
 */
#ifndef G2_TOUCH_RESET_CAPSENSE_CONTEXT_H
#define G2_TOUCH_RESET_CAPSENSE_CONTEXT_H

#include <stddef.h>

typedef struct {
 const void *ptrCommonConfig;
 void *ptrCommonContext;
 void *ptrInternalContext;
 const void *ptrWdConfig;
 void *ptrWdContext;
 const void *ptrPinConfig;
 const void *ptrShieldPinConfig;
 void *ptrActiveScanSns;
 void *ptrBistContext;
 void *ptrBaseFrameContext;
 void *ptrSensorFrameContext;
 void *ptrSensorFrameLpContext;
 const void *ptrScanSlots;
 const void *ptrLpScanSlots;
 void *ptrLpHistoricContext;
} touch_capsense_context_v6_lp;

_Static_assert(sizeof(touch_capsense_context_v6_lp)==60u,"v6 LP context ABI");
_Static_assert(offsetof(touch_capsense_context_v6_lp,ptrScanSlots)==0x30u,"slot ABI");
_Static_assert(offsetof(touch_capsense_context_v6_lp,ptrLpHistoricContext)==0x38u,"history ABI");

extern touch_capsense_context_v6_lp touch_reset_capsense_context;

#endif
