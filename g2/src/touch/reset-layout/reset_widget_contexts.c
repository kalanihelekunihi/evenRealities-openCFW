/* SPDX-License-Identifier: MIT
 * Product widget runtime settings, not executable bytes. Infineon CapSense
 * v6 LP/fine-CDAC ABI, corroborated by native60-byte widget indexing,
 * status byte35 and frame-generator compensation divider halfword54.
 * ROMb614 -> RAM20000548: three60-byte contexts; slider position at20000656.
 */
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
touch_reset_position touch_reset_slider_position
 __attribute__((section(".touch_init.slider_position"),used))={0u,0u,0u,0u};
touch_reset_widget_context touch_reset_widgets[3]
 __attribute__((section(".touch_init.widget_contexts"),used))={
 {.fingerCap=160u,.fingerTh=150u,.proxTh=200u,.lowBslnRst=30u,
  .snsClk=64u,.rowSnsClk=276u,.noiseTh=30u,.nNoiseTh=30u,.hysteresis=10u,
  .onDebounce=1u,.snsClkSource=2u,.bslnCoeff=1u,.numSubConversions=200u,
  .cdacRef=255u,.cdacFine=31u,.rowCdacFine=1u,.cicRate=255u,
  .cdacCompDivider=138u,.lfsrBits=128u,.cicShift=128u,.rowCicShift=128u},
 {.fingerCap=160u,.fingerTh=480u,.proxTh=100u,.lowBslnRst=30u,
  .snsClk=64u,.rowSnsClk=84u,.noiseTh=300u,.nNoiseTh=200u,.hysteresis=55u,
  .onDebounce=1u,.snsClkSource=2u,.bslnCoeff=1u,
  .wdTouch={&touch_reset_slider_position,1u},.numSubConversions=200u,
  .cdacRef=32u,.cicRate=255u,.cdacCompDivider=32u,
  .lfsrBits=128u,.cicShift=128u,.rowCicShift=128u},
 {.fingerCap=160u,.fingerTh=1000u,.proxTh=160u,.lowBslnRst=30u,
  .snsClk=28u,.rowSnsClk=104u,.noiseTh=40u,.nNoiseTh=40u,.hysteresis=10u,
  .onDebounce=3u,.snsClkSource=2u,.bslnCoeff=1u,.numSubConversions=360u,
  .cdacRef=255u,.cdacFine=31u,.rowCdacFine=1u,.cicRate=255u,
  .cdacCompDivider=28u,.lfsrBits=128u,.cicShift=128u,.rowCicShift=128u}
};
