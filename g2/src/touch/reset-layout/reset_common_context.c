/* SPDX-License-Identifier: MIT
 * Source-owned reset data at RAM20000528, ROMb5f4.
 * ABI: Infineon CapSense v4/v5/v6 fifth-generation LP common context.
 * Reference commit247a9a0f79eb976f144f5fbeb29488c1c2606517.
 * Native7e04 reset consumes tunerCmd(+2),tunerSt(+6),lpDataSt(+22),lpScanSt(+28);
 * native ILO consumer reads status(+8). Version7/11's wider ABI does not match.
 * configId is the authenticated product configuration fingerprint, not an
 * invented default or a claim of recovering its generator input.
 */
#include <stdint.h>
#include <stddef.h>
typedef struct {
 uint16_t configId,tunerCmd,scanCounter;
 uint8_t tunerSt,initDone;
 volatile uint32_t status;
 uint32_t timestampInterval,timestamp;
 uint8_t tunerCnt;
 uint16_t lpDataSt;
 uint8_t lpFirstSnsId,lpSnsNumber,lpNumFrame,lpScanCounter,lpScanSt;
} touch_reset_common_context;
_Static_assert(sizeof(touch_reset_common_context)==32u,"LP common ABI");
_Static_assert(offsetof(touch_reset_common_context,tunerCmd)==2u,"native tuner cmd");
_Static_assert(offsetof(touch_reset_common_context,tunerSt)==6u,"native tuner state");
_Static_assert(offsetof(touch_reset_common_context,status)==8u,"native ILO state");
_Static_assert(offsetof(touch_reset_common_context,lpDataSt)==22u,"native LP data");
_Static_assert(offsetof(touch_reset_common_context,lpScanSt)==28u,"native LP scan state");
touch_reset_common_context touch_reset_common
 __attribute__((section(".touch_init.common_context"),used)) = {
 .configId=0xc9b3u,.timestampInterval=1u
};
