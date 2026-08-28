/* SPDX-License-Identifier: MIT */
#include "runtime_clkmgr_divider_candidate.h"

#define OPEN_CFW_CLKMGR_UQ15_SCALE 32768.0f

uint32_t open_cfw_clkmgr_hfrc2_uq15_divider(
    uint32_t source_hz,
    uint32_t requested_hz,
    uint32_t source_divider_exponent,
    uint32_t *divider_uq15)
{
    uint32_t divided_source_hz;
    float coefficient;

    if (divider_uq15 == 0 || source_hz == 0U ||
        source_divider_exponent >= 32U)
        return OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT;
    divided_source_hz = source_hz >> source_divider_exponent;
    if (divided_source_hz == 0U)
        return OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT;

    coefficient = ((float)requested_hz / (float)divided_source_hz) *
                  OPEN_CFW_CLKMGR_UQ15_SCALE;
    if (!(coefficient >= 0.0f) || coefficient > 4294967040.0f)
        return OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT;
    *divider_uq15 = (uint32_t)coefficient;
    return OPEN_CFW_CLKMGR_DIVIDER_OK;
}

uint32_t open_cfw_clkmgr_hfrc_integer_divider(
    uint32_t source_hz,
    uint32_t requested_hz,
    uint32_t *divider)
{
    if (divider == 0 || source_hz == 0U)
        return OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT;
    *divider = requested_hz / source_hz;
    return OPEN_CFW_CLKMGR_DIVIDER_OK;
}
