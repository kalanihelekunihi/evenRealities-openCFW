/* SPDX-License-Identifier: MIT
 * Recovered LP configuration ABI: pinned Infineon CapSense 6.10 reference
 * 247a9a0f79eb976f144f5fbeb29488c1c2606517. Field layout only; vendor
 * source remains reference-only under its retained LICENSE. Product values
 * come from locked G2 s200_v2.2.6.10 Touch, not another board's generator.
 */
#ifndef TOUCH_GENERATED_COMMON_CONFIG_H
#define TOUCH_GENERATED_COMMON_CONFIG_H
#include <stdint.h>
#include <stddef.h>
#include "reset_pin_config.h"
struct touch_reset_lp_channel;
struct touch_common_config_lp {
    uint32_t cpuClkHz;
    uint32_t periClkHz;
        const struct touch_reset_lp_channel * ptrChConfig;
    uint16_t numPin;
    uint16_t numSns;
    uint16_t proxTouchCoeff;
    uint16_t csdRConst;
        uint16_t numEpiCycles;
        uint16_t numCoarseInitChargeCycles;
        uint16_t numCoarseInitSettleCycles;
        uint16_t numSlots;
        uint16_t numProWaitKrefDelayPrs;
        uint16_t numProWaitKrefDelay;
        uint16_t numEpiKrefDelayPrs;
        uint16_t numEpiKrefDelay;
    uint8_t numWd;
    uint8_t periDividerType;
    uint8_t periDividerIndex;
    uint8_t analogWakeupDelay;
    uint8_t swSensorAutoResetEn;
    uint8_t csdInactiveSnsConnection;
    uint8_t csxInactiveSnsConnection;
    uint8_t isxInactiveSnsConnection;
    uint8_t csdShieldNumPin;
    uint8_t csxRawTarget;
    uint8_t csxCalibrationError;
    uint8_t csdRawTarget;
    uint8_t csdCalibrationError;
        uint8_t isxRawTarget;
        uint8_t isxCalibrationError;
        uint8_t csdShieldMode;
        uint8_t numProOffsetCycles;
        uint8_t proOffsetCdacComp;
        uint8_t chopPolarity;
        uint8_t numBadScans;
        uint8_t counterMode;
};
struct touch_electrode_config_lp {
 const struct touch_pin_config *ptrPin;
 uint8_t type,numPins;
};
_Static_assert(sizeof(struct touch_common_config_lp)==60u,"LP common config");
_Static_assert(offsetof(struct touch_common_config_lp,ptrChConfig)==8u,"native channel");
_Static_assert(offsetof(struct touch_common_config_lp,numPin)==12u,"native pin count");
_Static_assert(offsetof(struct touch_common_config_lp,csdShieldNumPin)==44u,"native shield count");
_Static_assert(offsetof(struct touch_common_config_lp,numBadScans)==55u,"native counter options");
_Static_assert(sizeof(struct touch_electrode_config_lp)==8u,"native electrode stride");
_Static_assert(offsetof(struct touch_electrode_config_lp,numPins)==5u,"native mask consumer");
extern const struct touch_common_config_lp touch_generated_common_config;
extern const struct touch_electrode_config_lp touch_generated_electrodes[9];
#endif
