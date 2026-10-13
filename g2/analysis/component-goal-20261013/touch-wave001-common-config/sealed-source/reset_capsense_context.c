/* SPDX-License-Identifier: MIT
 * Experimental typed reset top-level CapSense context, RAM 0x200004ec.
 * Field order is cy_stc_capsense_context_t from pinned CapSense v6 LP.
 * Product config and generated runtime pointees remain external contracts.
 * The existing selected slot-link units own offsets 0x30 and 0x34 until this
 * whole context replaces them in a reconciled final linker graph.
 */
#include <stdint.h>
#include <stddef.h>
#include "reset_pin_config.h"
#include "reset_active_scan_context.h"
#include "reset_base_frame_context.h"
#include "reset_sensor_frames.h"
#include "reset_generated_common_config.h"
extern unsigned char touch_reset_common[];
extern unsigned char touch_generated_internal_context[];
extern const unsigned char touch_generated_widget_config[];
extern unsigned char touch_reset_widgets[];
extern const unsigned char touch_shield_pins_rom_b33c[];
extern unsigned char touch_reset_active_descriptors[];
extern unsigned char touch_reset_lp_descriptors[];
extern unsigned char touch_generated_lp_history[];
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
touch_capsense_context_v6_lp touch_reset_capsense_context
 __attribute__((section(".touch_init.capsense_context"),used)) = {
 .ptrCommonConfig=&touch_generated_common_config,
 .ptrCommonContext=touch_reset_common,
 .ptrInternalContext=touch_generated_internal_context,
 .ptrWdConfig=touch_generated_widget_config,
 .ptrWdContext=touch_reset_widgets,
 .ptrPinConfig=touch_generated_pin_config,
 .ptrShieldPinConfig=touch_shield_pins_rom_b33c,
 .ptrActiveScanSns=&touch_generated_active_scan_sns,
 .ptrBistContext=0,
 .ptrBaseFrameContext=&touch_generated_base_frame_context,
 .ptrSensorFrameContext=touch_generated_sensor_frame_context,
 .ptrSensorFrameLpContext=touch_generated_lp_sensor_frame_context,
 .ptrScanSlots=touch_reset_active_descriptors,
 .ptrLpScanSlots=touch_reset_lp_descriptors,
 .ptrLpHistoricContext=touch_generated_lp_history,
};
