/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the two unambiguous two-byte zero-fill
 * alignment cells in the BL-009 range, each sitting exactly between two
 * already source-routed Thumb functions:
 * - 0x0042E642..0x0042E644, between the event-object/task
 *   initialisation service and the callback dispatcher.
 * - 0x0042FFFE..0x00430000, between the constant mode-one adapter and
 *   the platform bring-up function.
 * Both are `00 00` with no original referent; they are 4-byte function
 * alignment padding reproduced here as explicit named cells.
 */
typedef unsigned char open_cfw_bl009_u8;

__attribute__((used))
const open_cfw_bl009_u8
open_cfw_bootloader_bl009_gap_align[4] = { 0x00u, 0x00u, 0x00u, 0x00u };
