/* SPDX-License-Identifier: MIT
 * Recovered CapSense v6 LP internal context with HW IIR enabled.
 * Reference commit 247a9a0f79eb976f144f5fbeb29488c1c2606517;
 * LP pin-state count14 is primary constant, not inferred from RAM gap.
 * Native timer6bd4 reads HW-IIR flag at118; frame generator uses pin map99.
 */
#ifndef TOUCH_GENERATED_INTERNAL_CONTEXT_H
#define TOUCH_GENERATED_INTERNAL_CONTEXT_H
#include <stdint.h>
#include <stddef.h>
#include "reset_active_scan_context.h"
typedef void (*touch_scan_callback)(touch_active_scan_sns_v6_lp *);
typedef void (*touch_context_callback)(void *);
typedef void (*touch_tuner_receive_callback)(uint8_t **,uint8_t **,void *);
struct touch_internal_context_lp {
    touch_scan_callback ptrSSCallback;
    touch_scan_callback ptrEOSCallback;
    touch_context_callback ptrTunerSendCallback;
    touch_tuner_receive_callback ptrTunerReceiveCallback;
    void (* ptrISRCallback)(void * context);
        touch_context_callback ptrEODsInitCallback;
            uint32_t snsCtlReg;
            uint32_t activeWakeupTimer;
            uint32_t activeWakeupTimerCycles;
            uint32_t wotScanInterval;
            uint32_t wotScanIntervalCycles;
            uint32_t iloCompensationFactor;
        uint16_t numCoarseInitChargeCycles;
        uint16_t numCoarseInitSettleCycles;
        uint16_t currentSlotIndex;
        uint16_t endSlotIndex;
        uint16_t numValidSlots;
        uint16_t firstValidSlot;
        uint16_t lfsrPoly;
            uint16_t numProWaitKrefDelayPrs;
            uint16_t numProWaitKrefDelay;
            uint16_t numEpiKrefDelayPrs;
            uint16_t numEpiKrefDelay;
            uint16_t numSlots;
            uint16_t startSlotIndex;
            uint16_t wotTimeout;
        uint8_t intrIsxInactSnsConn;
        uint8_t numFineInitCycles;
        uint8_t lfsrScale;
        uint8_t cdacDitherSeed;
        uint8_t cdacDitherPoly;
        uint8_t modClk;
        uint8_t scanSingleSlot;
        uint8_t numProOffsetCycles;
        uint8_t proOffsetCdacComp;
        uint8_t hwConfigState;
        uint8_t slotAutoCalibrMode;
        uint8_t intrCsdRawTarget;
        uint8_t intrCsxRawTarget;
        uint8_t intrIsxRawTarget;
            uint8_t csdCdacDitherEn;
            uint8_t csxCdacDitherEn;
            uint8_t isxCdacDitherEn;
            uint8_t bslnCoefSlow;
            uint8_t bslnCoefFast;
            uint8_t bslnUpdateDelay;
            uint8_t iirCoeffLp;
            uint8_t firstActSubFrame;
            uint8_t numFunc;
            uint8_t mapPinState[14];
            uint8_t operatingMode;
            uint8_t mrssStateAfterScan;
            uint8_t repeatScanEn;
    uint8_t intrCsdInactSnsConn;
    uint8_t intrCsxInactSnsConn;
        uint8_t hwIirInit;
};
_Static_assert(sizeof(struct touch_internal_context_lp)==120u,"LP internal ABI");
_Static_assert(offsetof(struct touch_internal_context_lp,ptrISRCallback)==16u,"native ISR slot");
_Static_assert(offsetof(struct touch_internal_context_lp,activeWakeupTimer)==28u,"native wakeup timer");
_Static_assert(offsetof(struct touch_internal_context_lp,startSlotIndex)==72u,"native active timer");
_Static_assert(offsetof(struct touch_internal_context_lp,mapPinState)==99u,"native pin map");
_Static_assert(offsetof(struct touch_internal_context_lp,operatingMode)==113u,"native mode");
_Static_assert(offsetof(struct touch_internal_context_lp,intrCsdInactSnsConn)==116u,"native scan prep");
_Static_assert(offsetof(struct touch_internal_context_lp,intrCsxInactSnsConn)==117u,"native scan prep");
_Static_assert(offsetof(struct touch_internal_context_lp,hwIirInit)==118u,"native active timer flag");
extern struct touch_internal_context_lp touch_generated_internal_context;
#endif
