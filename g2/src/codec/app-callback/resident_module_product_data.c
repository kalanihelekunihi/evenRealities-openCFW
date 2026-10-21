/* SPDX-License-Identifier: MIT
 * Typed image-A source data for module dispatch. Native source extents:
 * 0x100266e0..0x10026880 (26 records) and 0x10026880..0x100268c8
 * (three mode bytes plus 17 configuration words). Runtime placement at
 * matching 0x2002xxxx addresses remains a linker/scatter-copy obligation.
 */
#include "resident_product_data.h"
_Static_assert(sizeof(struct gx8002_module_config_data) == 72,
               "native module config ABI");

const struct gx8002_module_config_data gx8002_module_config_26880
    __attribute__((section(".gx8002.module_config.26880"), used,
                   aligned(4))) = {
    {0x24, 0x24, 0x28, 0x00},
    {0x003f0880, 0x003f1080, 0x003f1880, 0x003f1084,
     0x003f1884, 0x003f0084, 0x003f0080, 0x03ff0088,
     0x003f0884, 0x003f0c88, 0x003f1084, 0x003f0880,
     0x003f0884, 0x003f1080, 0x003f1880, 0x003f0084,
     0x003f0080}
};

_Static_assert(sizeof(struct gx8002_module_entry) == 16,
               "native module table ABI");

#define C(i) (&gx8002_module_config_26880.words[i])
#define M(i) (&gx8002_module_config_26880.modes[i])
const struct gx8002_module_entry gx8002_module_table_266e0[26]
    __attribute__((section(".gx8002.module_table.266e0"), used,
                   aligned(4))) = {
    { 0,  0,  1,   1, 0, C(0),  0},
    { 1,  2,  3,   3, 0, C(1),  0},
    { 2,  4,  5,   6, 0, C(2),  M(0)},
    { 3,  7,  8,   9, 0, C(3),  0},
    { 4,  9, 10,  10, 0, C(4),  0},
    { 5, 11, 12,  11, 0, C(5),  0},
    { 6, 13, 14,  12, 0, C(6),  0},
    { 7,  4,  6,  19, 0, C(7),  0},
    { 8,  4, 19,  20, 0, C(8),  0},
    { 9, 20, 21,  24, 0, C(9),  0},
    {10,  4, 12,   0, 0, C(10), 0},
    {16,  5,  5,   1, 0, 0,     M(1)},
    {17,  5, 24,   -1,0, 0,     0},
    {18,  5, 25,   -1,0, 0,     0},
    {11,  6, 26,   2, 0, 0,     M(2)},
    {19,  7,  7,   3, 0, C(11), 0},
    {20,  7, 28,   -1,0, 0,     0},
    {21,  7, 29,   -1,0, 0,     0},
    {12,  8,  8,   4, 0, C(12), 0},
    {13,  9,  9,   5, 0, C(13), 0},
    {14, 10, 10,   6, 0, C(14), 0},
    {15, 11, 11,   7, 0, C(15), 0},
    {22, 27, 27,  11, 0, C(16), 0},
    {23, 27, 22,   -1,0, 0,     0},
    {24, 27, 23,   -1,0, 0,     0},
    {25, -1, 14,   -1,0, 0,     0},
};
#undef C
#undef M
