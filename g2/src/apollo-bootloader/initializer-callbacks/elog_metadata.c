/* SPDX-License-Identifier: MIT
 * Six EasyLogger level labels and six ANSI color suffixes consumed through
 * the scatter-initialized pointer arrays at RAM +0x31c and +0x334.
 * Fixed row widths are authenticated by the stock ROM data consumers.
 */
#include <stdint.h>
__attribute__((section(".boot_elog_color_suffixes"), used))
const char opencfw_boot_elog_color_suffixes[6][8] = {
    "35;22m", "31;22m", "33;22m", "36;22m", "32;22m", "34;22m",
};
__attribute__((section(".boot_elog_level_suffixes"), used))
const char opencfw_boot_elog_level_suffixes[6][4] = {
    "A/", "E/", "W/", "I/", "D/", "V/",
};
_Static_assert(sizeof(opencfw_boot_elog_color_suffixes)==48,"color table size");
_Static_assert(sizeof(opencfw_boot_elog_level_suffixes)==24,"level table size");
