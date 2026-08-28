/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_control_candidate.h"

#define SC_RESV_MASK 0x00E0E0E0u
#define PAUSE_RESV 0x000000E0u

enum {
    R_APBCLK, R_SETCLR, R_IOMSEL, R_DCX, R_SCRAMBLE, R_XIPACK,
    R_CE_LATENCY, R_SDR250, R_DDR, R_DQS0, R_DQS1, R_RX0, R_RX1,
    R_TIMING0, R_TIMING1, R_XIP, R_AXI, R_XIP_MISC, R_ENDIAN,
    R_PAUSE, R_UNPAUSE, R_SEQ_LOOP, R_BLOCK, R_CQ_RAW,
    R_INSTR, R_ADDR, R_WRITE_LATENCY, R_XIP_MIXED, R_XIP_WRITE_LATENCY,
    R_SEND_ADDR, R_CPU_READ, R_SCRAMBLE_START, R_SCRAMBLE_END,
};

static int valid_handle(const open_cfw_mspi_control_state_t *s)
{
    return s && ((s->prefix & 0x01ffffffu) == OPEN_CFW_MSPI_HANDLE_PREFIX);
}

static int requires_config(uint32_t r)
{
    switch (r) {
    case 0: case 1: case 2: case 3: case 8: case 9: case 14: case 15:
    case 16: case 17: case 18: case 19: case 24: case 25: case 26:
    case 29: case 30: case 31: case 34: case 35: case 36: case 39:
        return 1;
    default:
        return 0;
    }
}

static uint32_t callback(uint32_t status, uint32_t *trace)
{
    ++*trace;
    return status;
}

uint32_t open_cfw_bootloader_mspi_control_candidate(
    open_cfw_mspi_control_state_t *s,
    uint32_t request,
    open_cfw_mspi_control_config_t *c)
{
    uint32_t r;
    uint32_t status;
    if (!valid_handle(s)) return OPEN_CFW_MSPI_INVALID_HANDLE;
    r = request & 0xffu;
    if (r >= 40u) return OPEN_CFW_MSPI_INVALID_ARG;
    if (!s->configured) return OPEN_CFW_MSPI_INVALID_OPERATION;
    if (requires_config(r) && !c) return OPEN_CFW_MSPI_INVALID_ARG;

    switch (r) {
    case 0:
        s->reg[R_APBCLK] = c->word[0] & 1u;
        break;
    case 1:
        if (c->word[0] & SC_RESV_MASK) return OPEN_CFW_MSPI_INVALID_ARG;
        s->reg[R_SETCLR] = c->word[0];
        break;
    case 2:
        if (c->word[0] >= 8u && c->word[0] != 7u) return OPEN_CFW_MSPI_INVALID_ARG;
        s->reg[R_IOMSEL] = c->word[0];
        break;
    case 3:
        if (c->word[0] >= 3u && c->word[0] != 7u) return OPEN_CFW_MSPI_INVALID_ARG;
        s->reg[R_IOMSEL] = c->word[0] + 8u;
        break;
    case 4: s->reg[R_DCX] = 0; break;
    case 5: s->reg[R_DCX] = 1; break;
    case 6: s->reg[R_SCRAMBLE] = 0; break;
    case 7: s->reg[R_SCRAMBLE] = 1; break;
    case 8: s->reg[R_XIPACK] = c->word[0] & 3u; break;
    case 9: s->reg[R_CE_LATENCY] = c->word[0] & 3u; break;
    case 10: s->reg[R_SDR250] = 0; break;
    case 11: s->reg[R_SDR250] = 1; break;
    case 12: s->reg[R_DDR] = 0; break;
    case 13: s->reg[R_DDR] = 1; break;
    case 14:
        s->reg[R_DQS0] = c->word[0];
        s->reg[R_DQS1] = c->word[1];
        break;
    case 15:
        s->reg[R_RX0] = c->word[0];
        s->reg[R_RX1] = c->word[1];
        break;
    case 16:
        s->reg[R_TIMING0] = c->word[0];
        s->reg[R_TIMING1] = c->word[1];
        break;
    case 17:
        c->word[0] = s->reg[R_TIMING0];
        c->word[1] = s->reg[R_TIMING1];
        break;
    case 18:
        status = callback(s->xip_check_status, &s->trace[0]);
        if (status) return status;
        s->reg[R_AXI] = c->word[0];
        s->reg[R_SCRAMBLE_START] = c->word[1] >> 16;
        s->reg[R_SCRAMBLE_END] = c->word[2] >> 16;
        break;
    case 19: s->reg[R_XIP_MISC] = c->word[0]; break;
    case 20:
        ++s->trace[1];
        s->reg[R_XIP] &= ~1u;
        break;
    case 21: s->reg[R_XIP] |= 1u; break;
    case 22:
        s->reg[R_ENDIAN] = 1;
        s->big_endian = 1;
        break;
    case 23:
        s->reg[R_ENDIAN] = 0;
        s->big_endian = 0;
        break;
    case 24:
        s->pio_config = c->word[0];
        ++s->trace[2];
        return OPEN_CFW_MSPI_SUCCESS;
    case 25:
        if ((s->module == 1u || s->module == 2u) &&
            (c->word[0] == 0u || c->word[0] == 1u || c->word[0] == 12u))
            return OPEN_CFW_MSPI_OUT_OF_RANGE;
        ++s->trace[3];
        if (s->clock_source != c->word[1]) {
            status = callback(s->clock_release_status, &s->trace[4]);
            if (status) return status;
            status = callback(s->clock_request_status, &s->trace[5]);
            if (status) return status;
        }
        s->clock_source = c->word[1];
        s->clock_frequency = c->word[0];
        ++s->trace[6];
        break;
    case 26:
        if ((s->module == 1u || s->module == 2u) &&
            (c->word[0] == 10u || c->word[0] == 11u))
            return OPEN_CFW_MSPI_OUT_OF_RANGE;
        s->device_config = c->word[0];
        ++s->trace[7];
        return OPEN_CFW_MSPI_SUCCESS;
    case 27:
        return callback(s->pause_status, &s->trace[8]);
    case 28:
        ++s->trace[9];
        s->reg[R_UNPAUSE] = 1;
        break;
    case 29: {
        uint32_t next = c->word[0] ? OPEN_CFW_MSPI_SEQ_UNDER_CONSTRUCTION : OPEN_CFW_MSPI_SEQ_NONE;
        if (!s->has_tcb) return OPEN_CFW_MSPI_INVALID_OPERATION;
        if (next == s->sequence) return OPEN_CFW_MSPI_SUCCESS;
        if (s->sequence == OPEN_CFW_MSPI_SEQ_RUNNING) {
            status = callback(s->pause_status, &s->trace[8]);
            if (status) return status;
        } else if (s->sequence == OPEN_CFW_MSPI_SEQ_NONE && s->cq_entries) {
            return OPEN_CFW_MSPI_INVALID_OPERATION;
        }
        ++s->trace[10];
        s->cq_entries = 0;
        s->cq_transactions = 0;
        s->unsolicited = 0;
        s->sequence = next;
        s->autonomous = 1;
        break;
    }
    case 30:
        if ((c->word[1] & PAUSE_RESV) || (c->word[2] & SC_RESV_MASK))
            return OPEN_CFW_MSPI_INVALID_ARG;
        if (s->sequence != OPEN_CFW_MSPI_SEQ_UNDER_CONSTRUCTION)
            return OPEN_CFW_MSPI_INVALID_OPERATION;
        s->block = 0;
        status = callback(s->allocation_status, &s->trace[11]);
        if (status) return status;
        status = callback(s->post_status, &s->trace[12]);
        if (status) return status;
        if (s->cq_entries++ == 0u) {
            status = callback(s->enable_status, &s->trace[13]);
            if (status) return status;
        }
        s->sequence = c->word[0] ? OPEN_CFW_MSPI_SEQ_RUNNING : OPEN_CFW_MSPI_SEQ_NONE;
        break;
    case 31:
        if (s->has_hp_transactions) return OPEN_CFW_MSPI_INVALID_OPERATION;
        if (!c->pointer[0] || c->word[0] < 24u) return OPEN_CFW_MSPI_INVALID_ARG;
        s->has_hp_transactions = 1;
        s->hp_entries = c->word[0] / 24u;
        break;
    case 32:
        s->reg[R_BLOCK] = 1;
        s->block = 1;
        s->hp_pending = 0;
        break;
    case 33:
        s->reg[R_BLOCK] = 0;
        s->block = 0;
        if (!s->hp_pending) {
            status = callback(s->schedule_status, &s->trace[14]);
            if (status) return status;
            s->hp_pending = 0;
        }
        break;
    case 34:
        if (!s->has_cmdq) return OPEN_CFW_MSPI_INVALID_OPERATION;
        if (s->cq_entries == OPEN_CFW_MSPI_MAX_CQ_ENTRIES)
            return OPEN_CFW_MSPI_OUT_OF_RANGE;
        status = callback(s->allocation_status, &s->trace[11]);
        if (status) return OPEN_CFW_MSPI_OUT_OF_RANGE;
        s->reg[R_CQ_RAW] = c->word[0];
        status = callback(s->post_status, &s->trace[12]);
        if (status) return status;
        if (s->cq_entries++ == 0u) {
            status = callback(s->enable_status, &s->trace[13]);
            if (status) return status;
        }
        ++s->cq_transactions;
        if (c->pointer[1]) {
            s->autonomous = 0;
            s->unsolicited = 0;
        } else {
            ++s->unsolicited;
        }
        break;
    case 35:
        if (c->word[0] > 4u || c->word[1] > 2u) return OPEN_CFW_MSPI_INVALID_ARG;
        s->reg[R_ADDR] = c->word[0];
        s->reg[R_INSTR] = c->word[1];
        break;
    case 36:
        s->reg[R_WRITE_LATENCY] = c->word[0];
        s->reg[R_XIP_MIXED] = 4;
        s->reg[R_XIP_WRITE_LATENCY] = c->word[1] & 1u;
        break;
    case 37: s->reg[R_SEND_ADDR] = 0; break;
    case 38: s->reg[R_SEND_ADDR] = 1; break;
    case 39:
        s->reg[R_CPU_READ] = c->word[0] ?
            (1u | ((c->word[1] & 3u) << 1) | ((c->word[2] & 7u) << 4)) : 0u;
        break;
    default:
        return OPEN_CFW_MSPI_INVALID_ARG;
    }
    return OPEN_CFW_MSPI_SUCCESS;
}
