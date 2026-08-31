/* SPDX-License-Identifier: MIT */
#include <stdint.h>

_Alignas(uint32_t) static uint8_t context_storage[0x120];
static uint8_t *context_pointer = context_storage;
static uint32_t start_result;
static uint32_t end_result;
static uint32_t error_value;
static uint32_t start_calls;
static uint32_t end_calls;
static uint32_t error_calls;

#define OPEN_CFW_NEMAVG_CONTEXT_CELL (&context_pointer)
#define OPEN_CFW_NEMAVG_DRAW_START_CAP host_draw_start_cap
#define OPEN_CFW_NEMAVG_DRAW_END_CAP host_draw_end_cap
#define OPEN_CFW_NEMAVG_SET_ERROR host_set_error

static uint32_t host_draw_start_cap(void)
{
    ++start_calls;
    return start_result;
}

static uint32_t host_draw_end_cap(void)
{
    ++end_calls;
    return end_result;
}

static void host_set_error(uint32_t error)
{
    ++error_calls;
    error_value = error;
}

#include "../../components/apollo_main/core_overlay/runtime_nemavg_draw_caps_dispatch.c"

static void reset_trace(void)
{
    start_result = 0U;
    end_result = 0U;
    error_value = 0U;
    start_calls = 0U;
    end_calls = 0U;
    error_calls = 0U;
    *(uint32_t *)(void *)(context_storage + 0x110U) = UINT32_C(0xA1A2A3A4);
    *(uint32_t *)(void *)(context_storage + 0x114U) = UINT32_C(0x11223344);
    *(uint32_t *)(void *)(context_storage + 0x118U) = UINT32_C(0x55667788);
    *(uint32_t *)(void *)(context_storage + 0x11CU) = UINT32_C(0xB1B2B3B4);
}

int main(void)
{
#define CHECK(value) do { if (!(value)) return __LINE__; } while (0)
    reset_trace();
    CHECK(open_cfw_nemavg_draw_caps_dispatch() == 0U);
    CHECK(start_calls == 1U && end_calls == 1U && error_calls == 0U);
    CHECK(*(uint32_t *)(void *)(context_storage + 0x114U) ==
          UINT32_C(0x11223344));

    reset_trace();
    start_result = UINT32_C(0x00800000);
    CHECK(open_cfw_nemavg_draw_caps_dispatch() == UINT32_C(0x00800000));
    CHECK(start_calls == 1U && end_calls == 0U && error_calls == 1U);
    CHECK(error_value == UINT32_C(0x00800000));
    CHECK(*(uint32_t *)(void *)(context_storage + 0x114U) == 0U);
    CHECK(*(uint32_t *)(void *)(context_storage + 0x118U) == 0U);
    CHECK(*(uint32_t *)(void *)(context_storage + 0x110U) ==
          UINT32_C(0xA1A2A3A4));
    CHECK(*(uint32_t *)(void *)(context_storage + 0x11CU) ==
          UINT32_C(0xB1B2B3B4));

    reset_trace();
    end_result = UINT32_C(0x00400000);
    CHECK(open_cfw_nemavg_draw_caps_dispatch() == UINT32_C(0x00400000));
    CHECK(start_calls == 1U && end_calls == 1U && error_calls == 1U);
    CHECK(error_value == UINT32_C(0x00400000));

    reset_trace();
    context_pointer = (uint8_t *)0;
    start_result = UINT32_C(0x00800000);
    CHECK(open_cfw_nemavg_draw_caps_dispatch() == UINT32_C(0x00800000));
    CHECK(error_calls == 1U);
    context_pointer = context_storage;
    return 0;
}
