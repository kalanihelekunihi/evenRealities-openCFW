/* SPDX-License-Identifier: MIT
 * Recovered 60-byte CapSense LP widget runtime contexts.
 */
#ifndef G2_TOUCH_RESET_WIDGET_CONTEXTS_H
#define G2_TOUCH_RESET_WIDGET_CONTEXTS_H

#include <stdint.h>
#include <stddef.h>

typedef struct {uint16_t x,y,z,id;} touch_reset_position;
typedef struct {touch_reset_position *ptrPosition;uint8_t numPosition;} touch_reset_touch;
typedef struct {
 uint16_t fingerCap,sigPFC,maxRawCount,maxRawCountRow,fingerTh,proxTh;
 uint16_t lowBslnRst,snsClk,rowSnsClk,gestureDetected,gestureDirection;
 int16_t xDelta,yDelta;
 uint16_t noiseTh,nNoiseTh,hysteresis;
 uint8_t onDebounce,snsClkSource,bslnCoeff,status;
 touch_reset_touch wdTouch;
 uint16_t numSubConversions;
 uint8_t cdacRef,rowCdacRef,cdacFine,rowCdacFine,cicRate,cdacDitherValue,coarseInitBypassEn;
 uint16_t cdacCompDivider;
 uint8_t lfsrBits,cicShift,rowCicShift;
} touch_reset_widget_context;

_Static_assert(sizeof(touch_reset_position)==8u,"vendor position");
_Static_assert(sizeof(touch_reset_widget_context)==60u,"native widget stride");
_Static_assert(offsetof(touch_reset_widget_context,status)==35u,"native widget status");
_Static_assert(offsetof(touch_reset_widget_context,wdTouch)==36u,"vendor position link");
_Static_assert(offsetof(touch_reset_widget_context,cdacCompDivider)==54u,"native divider");

extern touch_reset_position touch_reset_slider_position;
extern touch_reset_widget_context touch_reset_widgets[3];

#endif
