/* SPDX-License-Identifier: MIT
 * Source-owned character data behind initialized locale pointer fields.
 * Stock 0x417c62 is a NUL-only string; 0x415732 is '.' followed by NUL.
 */
__attribute__((used, section(".boot_locale_empty")))
const char opencfw_boot_locale_empty[1] = {0};

__attribute__((used, section(".boot_locale_decimal_point")))
const char opencfw_boot_locale_decimal_point[2] = {'.', 0};
