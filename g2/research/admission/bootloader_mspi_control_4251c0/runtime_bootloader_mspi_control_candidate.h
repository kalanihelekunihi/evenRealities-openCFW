/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_CONTROL_CANDIDATE_H
#define OPEN_CFW_BOOTLOADER_MSPI_CONTROL_CANDIDATE_H

#include <stdint.h>

enum {
    OPEN_CFW_MSPI_SUCCESS = 0,
    OPEN_CFW_MSPI_INVALID_HANDLE = 2,
    OPEN_CFW_MSPI_OUT_OF_RANGE = 5,
    OPEN_CFW_MSPI_INVALID_ARG = 6,
    OPEN_CFW_MSPI_INVALID_OPERATION = 7,
    OPEN_CFW_MSPI_HANDLE_PREFIX = 0x01BEBEBEu,
    OPEN_CFW_MSPI_SEQ_NONE = 0,
    OPEN_CFW_MSPI_SEQ_UNDER_CONSTRUCTION = 1,
    OPEN_CFW_MSPI_SEQ_RUNNING = 2,
    OPEN_CFW_MSPI_MAX_CQ_ENTRIES = 32,
};

typedef struct {
    uint32_t word[8];
    uint8_t byte[16];
    uintptr_t pointer[2];
} open_cfw_mspi_control_config_t;

typedef struct {
    uint32_t prefix;
    uint32_t module;
    uint32_t configured;
    uint32_t reg[48];
    uint32_t pio_config;
    uint32_t device_config;
    uint32_t clock_frequency;
    uint32_t clock_source;
    uint32_t big_endian;
    uint32_t has_tcb;
    uint32_t has_cmdq;
    uint32_t cmdq_in_tcm;
    uint32_t sequence;
    uint32_t cq_entries;
    uint32_t cq_transactions;
    uint32_t unsolicited;
    uint32_t max_pending;
    uint32_t autonomous;
    uint32_t has_hp_transactions;
    uint32_t hp_entries;
    uint32_t hp_pending;
    uint32_t block;
    uint32_t pause_status;
    uint32_t allocation_status;
    uint32_t post_status;
    uint32_t enable_status;
    uint32_t schedule_status;
    uint32_t xip_check_status;
    uint32_t clock_release_status;
    uint32_t clock_request_status;
    uint32_t trace[16];
} open_cfw_mspi_control_state_t;

uint32_t open_cfw_bootloader_mspi_control_candidate(
    open_cfw_mspi_control_state_t *state,
    uint32_t request,
    open_cfw_mspi_control_config_t *config);

#endif
