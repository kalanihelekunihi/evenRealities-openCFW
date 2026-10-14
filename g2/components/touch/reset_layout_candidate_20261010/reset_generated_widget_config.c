/* SPDX-License-Identifier: MIT
 * Authored ABI transcription of three locked G2 Touch widget records.
 * Field offsets match pinned Infineon CapSense 5.0 LP type at commit
 * a4aa9306f7e4323994902f0baf5b1570ffbbfe59. Fixed stock pointers
 * require linker placement and product configuration validation.
 */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t ptrWdContext;
    uint32_t ptrSnsContext;
    uint32_t ptrEltdConfig;
    uint32_t ptrEltdCapacitance;
    uint32_t ptrSnsCapacitance;
    uint32_t ptrBslnInv;
    uint32_t ptrNoiseEnvelope;
    uint32_t ptrRawFilterHistory;
    uint32_t ptrRawFilterHistoryLow;
    uint32_t iirCoeff;
    uint32_t ptrDebounceArr;
    uint32_t ptrDiplexTable;
    uint32_t centroidConfig;
    uint16_t xResolution;
    uint16_t yResolution;
    uint16_t numSns;
    uint8_t numCols;
    uint8_t numRows;
    uint32_t ptrPosFilterHistory;
    uint32_t ptrCsxTouchHistory;
    uint32_t ptrCsxTouchBuffer;
    uint32_t ptrCsdTouchBuffer;
    uint32_t ptrGestureConfig;
    uint32_t ptrGestureContext;
    uint8_t ballisticConfig[8];
    uint32_t ptrBallisticContext;
    uint8_t aiirConfig[8];
    uint8_t advConfig[8];
    uint32_t posFilterConfig;
    uint16_t rawFilterConfig;
    uint16_t alpOnThreshold;
    uint16_t alpOffThreshold;
    uint8_t senseMethod;
    uint8_t wdType;
    uint32_t ptrMpTable;
    uint16_t firstSlotId;
    uint16_t numSlots;
    uint8_t numChopCycles;
    uint8_t mpOrder;
    uint8_t mpOrderRows;
    uint8_t lfsrDitherLimit;
    uint8_t snsClkSourceAutoSelMode;
    uint8_t mfsConfig;
    uint8_t cdacDitherScaleMode;
    uint8_t cicRateMode;
    uint8_t iirCoeffHw;
    uint8_t reserved_padding_after_iirCoeffHw;
    uint16_t cdacConfig;
} touch_widget_config_abi;
_Static_assert(sizeof(touch_widget_config_abi) == 144, "widget stride");
_Static_assert(offsetof(touch_widget_config_abi, ptrWdContext) == 0, "ptrWdContext offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrSnsContext) == 4, "ptrSnsContext offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrEltdConfig) == 8, "ptrEltdConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrEltdCapacitance) == 12, "ptrEltdCapacitance offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrSnsCapacitance) == 16, "ptrSnsCapacitance offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrBslnInv) == 20, "ptrBslnInv offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrNoiseEnvelope) == 24, "ptrNoiseEnvelope offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrRawFilterHistory) == 28, "ptrRawFilterHistory offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrRawFilterHistoryLow) == 32, "ptrRawFilterHistoryLow offset");
_Static_assert(offsetof(touch_widget_config_abi, iirCoeff) == 36, "iirCoeff offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrDebounceArr) == 40, "ptrDebounceArr offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrDiplexTable) == 44, "ptrDiplexTable offset");
_Static_assert(offsetof(touch_widget_config_abi, centroidConfig) == 48, "centroidConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, xResolution) == 52, "xResolution offset");
_Static_assert(offsetof(touch_widget_config_abi, yResolution) == 54, "yResolution offset");
_Static_assert(offsetof(touch_widget_config_abi, numSns) == 56, "numSns offset");
_Static_assert(offsetof(touch_widget_config_abi, numCols) == 58, "numCols offset");
_Static_assert(offsetof(touch_widget_config_abi, numRows) == 59, "numRows offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrPosFilterHistory) == 60, "ptrPosFilterHistory offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrCsxTouchHistory) == 64, "ptrCsxTouchHistory offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrCsxTouchBuffer) == 68, "ptrCsxTouchBuffer offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrCsdTouchBuffer) == 72, "ptrCsdTouchBuffer offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrGestureConfig) == 76, "ptrGestureConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrGestureContext) == 80, "ptrGestureContext offset");
_Static_assert(offsetof(touch_widget_config_abi, ballisticConfig) == 84, "ballisticConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrBallisticContext) == 92, "ptrBallisticContext offset");
_Static_assert(offsetof(touch_widget_config_abi, aiirConfig) == 96, "aiirConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, advConfig) == 104, "advConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, posFilterConfig) == 112, "posFilterConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, rawFilterConfig) == 116, "rawFilterConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, alpOnThreshold) == 118, "alpOnThreshold offset");
_Static_assert(offsetof(touch_widget_config_abi, alpOffThreshold) == 120, "alpOffThreshold offset");
_Static_assert(offsetof(touch_widget_config_abi, senseMethod) == 122, "senseMethod offset");
_Static_assert(offsetof(touch_widget_config_abi, wdType) == 123, "wdType offset");
_Static_assert(offsetof(touch_widget_config_abi, ptrMpTable) == 124, "ptrMpTable offset");
_Static_assert(offsetof(touch_widget_config_abi, firstSlotId) == 128, "firstSlotId offset");
_Static_assert(offsetof(touch_widget_config_abi, numSlots) == 130, "numSlots offset");
_Static_assert(offsetof(touch_widget_config_abi, numChopCycles) == 132, "numChopCycles offset");
_Static_assert(offsetof(touch_widget_config_abi, mpOrder) == 133, "mpOrder offset");
_Static_assert(offsetof(touch_widget_config_abi, mpOrderRows) == 134, "mpOrderRows offset");
_Static_assert(offsetof(touch_widget_config_abi, lfsrDitherLimit) == 135, "lfsrDitherLimit offset");
_Static_assert(offsetof(touch_widget_config_abi, snsClkSourceAutoSelMode) == 136, "snsClkSourceAutoSelMode offset");
_Static_assert(offsetof(touch_widget_config_abi, mfsConfig) == 137, "mfsConfig offset");
_Static_assert(offsetof(touch_widget_config_abi, cdacDitherScaleMode) == 138, "cdacDitherScaleMode offset");
_Static_assert(offsetof(touch_widget_config_abi, cicRateMode) == 139, "cicRateMode offset");
_Static_assert(offsetof(touch_widget_config_abi, iirCoeffHw) == 140, "iirCoeffHw offset");
_Static_assert(offsetof(touch_widget_config_abi, cdacConfig) == 142, "cdacConfig offset");

const touch_widget_config_abi touch_generated_widget_config[3]
    __attribute__((section(".touch_rodata.widget_config"), used)) = {
    {
        .ptrWdContext = 0x20000548u,
        .ptrSnsContext = 0x200005fcu,
        .ptrEltdConfig = 0xb2e4u,
        .ptrEltdCapacitance = 0x0u,
        .ptrSnsCapacitance = 0x0u,
        .ptrBslnInv = 0x0u,
        .ptrNoiseEnvelope = 0x0u,
        .ptrRawFilterHistory = 0x0u,
        .ptrRawFilterHistoryLow = 0x0u,
        .iirCoeff = 0x40u,
        .ptrDebounceArr = 0x200009f4u,
        .ptrDiplexTable = 0x0u,
        .centroidConfig = 0x0u,
        .xResolution = 0x0u,
        .yResolution = 0x0u,
        .numSns = 0x4u,
        .numCols = 0x4u,
        .numRows = 0x0u,
        .ptrPosFilterHistory = 0x0u,
        .ptrCsxTouchHistory = 0x0u,
        .ptrCsxTouchBuffer = 0x0u,
        .ptrCsdTouchBuffer = 0x0u,
        .ptrGestureConfig = 0x0u,
        .ptrGestureContext = 0x0u,
        .ballisticConfig = {0x09, 0x02, 0x04, 0x03, 0x04, 0x00, 0x00, 0x00},
        .ptrBallisticContext = 0x0u,
        .aiirConfig = {0x3c, 0x01, 0x03, 0x07, 0x0c, 0x40, 0x00, 0x00},
        .advConfig = {0x64, 0x00, 0x64, 0x00, 0x05, 0x00, 0x00, 0x00},
        .posFilterConfig = 0x0u,
        .rawFilterConfig = 0x0u,
        .alpOnThreshold = 0xfu,
        .alpOffThreshold = 0x5u,
        .senseMethod = 0x1u,
        .wdType = 0x7u,
        .ptrMpTable = 0x0u,
        .firstSlotId = 0x0u,
        .numSlots = 0x4u,
        .numChopCycles = 0x1u,
        .mpOrder = 0x1u,
        .mpOrderRows = 0x1u,
        .lfsrDitherLimit = 0xau,
        .snsClkSourceAutoSelMode = 0x0u,
        .mfsConfig = 0x0u,
        .cdacDitherScaleMode = 0x2u,
        .cicRateMode = 0x1u,
        .iirCoeffHw = 0x1u,
        .cdacConfig = 0x1aau,
    },
    {
        .ptrWdContext = 0x20000584u,
        .ptrSnsContext = 0x20000624u,
        .ptrEltdConfig = 0xb304u,
        .ptrEltdCapacitance = 0x0u,
        .ptrSnsCapacitance = 0x0u,
        .ptrBslnInv = 0x0u,
        .ptrNoiseEnvelope = 0x0u,
        .ptrRawFilterHistory = 0x0u,
        .ptrRawFilterHistoryLow = 0x0u,
        .iirCoeff = 0x40u,
        .ptrDebounceArr = 0x200009f8u,
        .ptrDiplexTable = 0x0u,
        .centroidConfig = 0x1u,
        .xResolution = 0xc8u,
        .yResolution = 0x0u,
        .numSns = 0x4u,
        .numCols = 0x4u,
        .numRows = 0x0u,
        .ptrPosFilterHistory = 0x20000848u,
        .ptrCsxTouchHistory = 0x0u,
        .ptrCsxTouchBuffer = 0x0u,
        .ptrCsdTouchBuffer = 0x0u,
        .ptrGestureConfig = 0x0u,
        .ptrGestureContext = 0x0u,
        .ballisticConfig = {0x09, 0x02, 0x04, 0x03, 0x04, 0x00, 0x00, 0x00},
        .ptrBallisticContext = 0x0u,
        .aiirConfig = {0x3c, 0x01, 0x03, 0x07, 0x0c, 0x40, 0x00, 0x00},
        .advConfig = {0x64, 0x00, 0x64, 0x00, 0x05, 0x00, 0x00, 0x00},
        .posFilterConfig = 0x800102u,
        .rawFilterConfig = 0x6000u,
        .alpOnThreshold = 0xfu,
        .alpOffThreshold = 0x5u,
        .senseMethod = 0x1u,
        .wdType = 0x2u,
        .ptrMpTable = 0x0u,
        .firstSlotId = 0x0u,
        .numSlots = 0x4u,
        .numChopCycles = 0x1u,
        .mpOrder = 0x1u,
        .mpOrderRows = 0x1u,
        .lfsrDitherLimit = 0xau,
        .snsClkSourceAutoSelMode = 0x0u,
        .mfsConfig = 0x0u,
        .cdacDitherScaleMode = 0x2u,
        .cicRateMode = 0x1u,
        .iirCoeffHw = 0x1u,
        .cdacConfig = 0x1a1u,
    },
    {
        .ptrWdContext = 0x200005c0u,
        .ptrSnsContext = 0x2000064cu,
        .ptrEltdConfig = 0xb324u,
        .ptrEltdCapacitance = 0x0u,
        .ptrSnsCapacitance = 0x0u,
        .ptrBslnInv = 0x0u,
        .ptrNoiseEnvelope = 0x0u,
        .ptrRawFilterHistory = 0x200009e8u,
        .ptrRawFilterHistoryLow = 0x200009e4u,
        .iirCoeff = 0x40u,
        .ptrDebounceArr = 0x200009f9u,
        .ptrDiplexTable = 0x0u,
        .centroidConfig = 0x0u,
        .xResolution = 0x0u,
        .yResolution = 0x0u,
        .numSns = 0x1u,
        .numCols = 0x1u,
        .numRows = 0x0u,
        .ptrPosFilterHistory = 0x0u,
        .ptrCsxTouchHistory = 0x0u,
        .ptrCsxTouchBuffer = 0x0u,
        .ptrCsdTouchBuffer = 0x0u,
        .ptrGestureConfig = 0x0u,
        .ptrGestureContext = 0x0u,
        .ballisticConfig = {0x09, 0x02, 0x04, 0x03, 0x04, 0x00, 0x00, 0x00},
        .ptrBallisticContext = 0x0u,
        .aiirConfig = {0x3c, 0x01, 0x03, 0x07, 0x0c, 0x40, 0x00, 0x00},
        .advConfig = {0x64, 0x00, 0x64, 0x00, 0x05, 0x00, 0x00, 0x00},
        .posFilterConfig = 0x0u,
        .rawFilterConfig = 0x3696u,
        .alpOnThreshold = 0x4bu,
        .alpOffThreshold = 0x19u,
        .senseMethod = 0x1u,
        .wdType = 0x6u,
        .ptrMpTable = 0x0u,
        .firstSlotId = 0x4u,
        .numSlots = 0x1u,
        .numChopCycles = 0x1u,
        .mpOrder = 0x1u,
        .mpOrderRows = 0x1u,
        .lfsrDitherLimit = 0xau,
        .snsClkSourceAutoSelMode = 0x0u,
        .mfsConfig = 0x0u,
        .cdacDitherScaleMode = 0x1u,
        .cicRateMode = 0x1u,
        .iirCoeffHw = 0x4u,
        .cdacConfig = 0x115u,
    },
};
