/* SPDX-License-Identifier: MIT
 * Runtime sensor frames at 0x200009fc and 0x20000aac. The pinned LP source
 * indexes LP frames by CY_MSCLP_11_SNS_REGS=11. The active frame stride is
 * seven words in the authenticated five-slot layout. Stock CRT clears both.
 */
#include "reset_sensor_frames.h"
_Static_assert(sizeof(touch_generated_lp_sensor_frame_context)==176u,"LP frames ABI");
_Static_assert(sizeof(touch_generated_sensor_frame_context)==140u,"active frames ABI");
uint32_t touch_generated_lp_sensor_frame_context[4][11]
 __attribute__((section(".bss.touch_lp_sensor_frames"),used));
uint32_t touch_generated_sensor_frame_context[5][7]
 __attribute__((section(".bss.touch_active_sensor_frames"),used));
