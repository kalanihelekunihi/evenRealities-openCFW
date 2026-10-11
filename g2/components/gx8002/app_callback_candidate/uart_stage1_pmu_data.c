/* SPDX-License-Identifier: MIT
 * Semantic source for the stage-1 PMU table at RAM 0x20002018 and auxiliary
 * register fields at 0x20002228. Entries come from the authenticated UART
 * stage-1 initialized-data image, with pointer fields emitted as relocations.
 */
#include "uart_stage1_pmu.h"

struct stage1_pmu_aux_data {
    uint8_t special_bits[4];
    struct stage1_pmu_aux_field fields[17];
};
_Static_assert(sizeof(struct stage1_pmu_aux_data) == 72, "PMU aux size");

__attribute__((section(".stage1.pmu.aux"), used))
const struct stage1_pmu_aux_data g2_uart_stage1_pmu_aux = {
    .special_bits = {0x24, 0x24, 0x28, 0},
    .fields = {
        {0x80, 0x08, 0x003f}, {0x80, 0x10, 0x003f},
        {0x80, 0x18, 0x003f}, {0x84, 0x10, 0x003f},
        {0x84, 0x18, 0x003f}, {0x84, 0x00, 0x003f},
        {0x80, 0x00, 0x003f}, {0x88, 0x00, 0x03ff},
        {0x84, 0x08, 0x003f}, {0x88, 0x0c, 0x003f},
        {0x84, 0x10, 0x003f}, {0x80, 0x08, 0x003f},
        {0x84, 0x08, 0x003f}, {0x80, 0x10, 0x003f},
        {0x80, 0x18, 0x003f}, {0x84, 0x00, 0x003f},
        {0x80, 0x00, 0x003f},
    },
};

#define AUX(i) (&g2_uart_stage1_pmu_aux.fields[i])
#define SPECIAL(i) (&g2_uart_stage1_pmu_aux.special_bits[i])
#define ENTRY(id,power,status,gate,aux,special) \
    {id, power, status, gate, 0, aux, special}

__attribute__((section(".stage1.pmu.table"), used))
const struct stage1_pmu_entry g2_uart_stage1_pmu_table[26] = {
    ENTRY(0,   0,  1,  1, AUX(0),  0),
    ENTRY(1,   2,  3,  3, AUX(1),  0),
    ENTRY(2,   4,  5,  6, AUX(2),  SPECIAL(0)),
    ENTRY(3,   7,  8,  9, AUX(3),  0),
    ENTRY(4,   9, 10, 10, AUX(4),  0),
    ENTRY(5,  11, 12, 11, AUX(5),  0),
    ENTRY(6,  13, 14, 12, AUX(6),  0),
    ENTRY(7,   4,  6, 19, AUX(7),  0),
    ENTRY(8,   4, 19, 20, AUX(8),  0),
    ENTRY(9,  20, 21, 24, AUX(9),  0),
    ENTRY(10,  4, 12,  0, AUX(10), 0),
    ENTRY(16,  5,  5,  1, 0,       SPECIAL(1)),
    ENTRY(17,  5, 24,255, 0,       0),
    ENTRY(18,  5, 25,255, 0,       0),
    ENTRY(11,  6, 26,  2, 0,       SPECIAL(2)),
    ENTRY(19,  7,  7,  3, AUX(11), 0),
    ENTRY(20,  7, 28,255, 0,       0),
    ENTRY(21,  7, 29,255, 0,       0),
    ENTRY(12,  8,  8,  4, AUX(12), 0),
    ENTRY(13,  9,  9,  5, AUX(13), 0),
    ENTRY(14, 10, 10,  6, AUX(14), 0),
    ENTRY(15, 11, 11,  7, AUX(15), 0),
    ENTRY(22, 27, 27, 11, AUX(16), 0),
    ENTRY(23, 27, 22,255, 0,       0),
    ENTRY(24, 27, 23,255, 0,       0),
    ENTRY(25,255, 14,255, 0,       0),
};
