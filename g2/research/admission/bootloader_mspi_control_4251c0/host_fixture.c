/* SPDX-License-Identifier: BSD-3-Clause */
#include <string.h>
#include "runtime_bootloader_mspi_control_candidate.h"

static open_cfw_mspi_control_state_t state;
static open_cfw_mspi_control_config_t config;

void open_cfw_test_control_reset(void)
{
    memset(&state, 0, sizeof(state));
    memset(&config, 0, sizeof(config));
    state.prefix = OPEN_CFW_MSPI_HANDLE_PREFIX;
    state.configured = 1;
    state.has_tcb = 1;
    state.has_cmdq = 1;
    state.max_pending = 16;
    state.autonomous = 1;
    config.pointer[0] = 1;
    config.word[0] = 24;
}

uint32_t open_cfw_test_control_run(uint32_t request, uint32_t have_config)
{
    return open_cfw_bootloader_mspi_control_candidate(
        &state, request, have_config ? &config : 0);
}

uint32_t open_cfw_test_control_run_valid(uint32_t request)
{
    open_cfw_test_control_reset();
    config.word[0] = 0;
    if ((request & 0xffu) == 30u) state.sequence = OPEN_CFW_MSPI_SEQ_UNDER_CONSTRUCTION;
    if ((request & 0xffu) == 31u) {
        config.word[0] = 24;
        config.pointer[0] = 1;
    }
    if ((request & 0xffu) == 35u) {
        config.word[0] = 4;
        config.word[1] = 2;
    }
    return open_cfw_bootloader_mspi_control_candidate(&state, request, &config);
}

void open_cfw_test_control_set_state(uint32_t index, uint32_t value)
{
    uint32_t *words = (uint32_t *)&state;
    if (index < sizeof(state) / sizeof(uint32_t)) words[index] = value;
}

uint32_t open_cfw_test_control_get_state(uint32_t index)
{
    uint32_t *words = (uint32_t *)&state;
    return index < sizeof(state) / sizeof(uint32_t) ? words[index] : 0;
}

void open_cfw_test_control_set_config(uint32_t index, uint32_t value)
{
    if (index < 8) config.word[index] = value;
}

uint32_t open_cfw_test_control_get_config(uint32_t index)
{
    return index < 8 ? config.word[index] : 0;
}

uint32_t open_cfw_test_control_reg(uint32_t index)
{
    return index < 48 ? state.reg[index] : 0;
}

uint32_t open_cfw_test_control_trace(uint32_t index)
{
    return index < 16 ? state.trace[index] : 0;
}

void open_cfw_test_control_set_core(uint32_t index, uint32_t value)
{
    switch (index) {
    case 0: state.prefix = value; break;
    case 1: state.configured = value; break;
    case 2: state.module = value; break;
    case 3: state.has_tcb = value; break;
    case 4: state.has_cmdq = value; break;
    case 5: state.sequence = value; break;
    case 6: state.cq_entries = value; break;
    case 7: state.has_hp_transactions = value; break;
    case 8: state.hp_pending = value; break;
    case 9: state.pause_status = value; break;
    case 10: state.allocation_status = value; break;
    case 11: state.post_status = value; break;
    case 12: state.enable_status = value; break;
    case 13: state.schedule_status = value; break;
    case 14: state.xip_check_status = value; break;
    case 15: state.clock_release_status = value; break;
    case 16: state.clock_request_status = value; break;
    default: break;
    }
}

uint32_t open_cfw_test_control_get_core(uint32_t index)
{
    switch (index) {
    case 0: return state.prefix;
    case 1: return state.configured;
    case 2: return state.module;
    case 3: return state.has_tcb;
    case 4: return state.has_cmdq;
    case 5: return state.sequence;
    case 6: return state.cq_entries;
    case 7: return state.has_hp_transactions;
    case 8: return state.hp_pending;
    case 9: return state.block;
    case 10: return state.pio_config;
    case 11: return state.device_config;
    case 12: return state.clock_frequency;
    case 13: return state.big_endian;
    case 14: return state.cq_transactions;
    default: return 0;
    }
}
