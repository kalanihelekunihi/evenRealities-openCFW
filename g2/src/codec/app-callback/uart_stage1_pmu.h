/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_UART_STAGE1_PMU_H
#define OPENCFW_UART_STAGE1_PMU_H
#include <stdint.h>
#include <stddef.h>

struct stage1_pmu_aux_field {
    uint8_t register_offset;
    uint8_t shift;
    uint16_t mask;
};
_Static_assert(sizeof(struct stage1_pmu_aux_field) == 4, "PMU aux ABI");

struct stage1_pmu_entry {
    uint32_t selector;
    uint8_t power_bit;
    uint8_t status_bit;
    uint8_t gate_bit;
    uint8_t reserved;
    const struct stage1_pmu_aux_field *aux;
    const uint8_t *special;
};
_Static_assert(sizeof(struct stage1_pmu_entry) == 16, "PMU table ABI");

struct stage1_pmu_view {
    const volatile uint8_t *entry;
    volatile uint32_t *base;
    volatile uint32_t *status;
    volatile uint32_t *set;
    volatile uint32_t *clear;
    volatile uint32_t *enable;
};
_Static_assert(sizeof(struct stage1_pmu_view) == 24, "PMU view ABI");

int32_t gx8002_uart_stage1_pmu_fill_desc(uint32_t selector,
                                           struct stage1_pmu_view *out);
int32_t gx8002_uart_stage2_pmu_fill_desc(uint32_t selector,
                                           struct stage1_pmu_view *out);
#endif
