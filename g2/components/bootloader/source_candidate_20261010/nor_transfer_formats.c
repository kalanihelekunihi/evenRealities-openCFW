/* SPDX-License-Identifier: MIT
 * Formatter inputs from authenticated Boot data at 0x431420 and 0x431468.
 * These strings are reached on MSPI transfer failure paths.
 */
const char opencfw_nor_read_transfer_format[] =
    "MSPI read xfer failed: instr=0x%02X, addr=0x%08X, len=%u, hal_st=%d\n";
const char opencfw_nor_write_transfer_format[] =
    "MSPI write xfer failed: instr=0x%02X, addr=0x%08X, len=%u, hal_st=%d\n";
