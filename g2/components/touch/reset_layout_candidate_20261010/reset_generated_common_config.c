/* SPDX-License-Identifier: MIT
 * ROM 0xb2a8..0xb2e4 common config, followed by nine typed electrodes
 * 0xb2e4..0xb32c. No executable bytes or guessed allocation extents.
 * Locked product values; stock-compatible recovery, no upstream fixes.
 */
#include "reset_generated_common_config.h"
extern struct touch_reset_lp_channel touch_reset_channel;
const struct touch_common_config_lp touch_generated_common_config
 __attribute__((section(".touch_rom.common_config"),used))={
 .cpuClkHz=48000000u,
 .periClkHz=0u,
 .ptrChConfig=&touch_reset_channel,
 .numPin=5u,
 .numSns=9u,
 .proxTouchCoeff=300u,
 .csdRConst=1000u,
 .numEpiCycles=0u,
 .numCoarseInitChargeCycles=200u,
 .numCoarseInitSettleCycles=200u,
 .numSlots=9u,
 .numProWaitKrefDelayPrs=16u,
 .numProWaitKrefDelay=2u,
 .numEpiKrefDelayPrs=96u,
 .numEpiKrefDelay=2u,
 .numWd=3u,
 .periDividerType=0u,
 .periDividerIndex=0u,
 .analogWakeupDelay=25u,
 .swSensorAutoResetEn=0u,
 .csdInactiveSnsConnection=4u,
 .csxInactiveSnsConnection=1u,
 .isxInactiveSnsConnection=2u,
 .csdShieldNumPin=2u,
 .csxRawTarget=40u,
 .csxCalibrationError=20u,
 .csdRawTarget=70u,
 .csdCalibrationError=10u,
 .isxRawTarget=40u,
 .isxCalibrationError=20u,
 .csdShieldMode=1u,
 .numProOffsetCycles=50u,
 .proOffsetCdacComp=32u,
 .chopPolarity=0u,
 .numBadScans=0u,
 .counterMode=0u,
};
const struct touch_electrode_config_lp touch_generated_electrodes[9]
 __attribute__((section(".touch_rom.electrodes"),used))={
 {&touch_generated_pin_config[0],0u,1u},
 {&touch_generated_pin_config[1],0u,1u},
 {&touch_generated_pin_config[2],0u,1u},
 {&touch_generated_pin_config[3],0u,1u},
 {&touch_generated_pin_config[0],0u,1u},
 {&touch_generated_pin_config[1],0u,1u},
 {&touch_generated_pin_config[2],0u,1u},
 {&touch_generated_pin_config[3],0u,1u},
 {&touch_generated_pin_config[4],0u,1u},
};
