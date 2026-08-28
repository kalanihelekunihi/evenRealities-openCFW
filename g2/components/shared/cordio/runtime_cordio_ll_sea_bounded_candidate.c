/*
 * SPDX-License-Identifier: Apache-2.0
 * Copyright (c) 2026 OpenCFW Contributors
 */

#include "runtime_cordio_ll_sea_bounded_candidate.h"

static const struct open_cfw_cordio_ll_sea_external_evidence
open_cfw_cordio_ll_sea_external_spans[OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_COUNT] = {
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D2418, 0x005d2418u, 0x005d280eu, 1014u,
      "4abad2e8a2bc331f0b27b8cc6e8f5055a4920cb29d765ff5ace44c257bf8ca6a" },
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D2A18, 0x005d2a18u, 0x005d2baeu, 406u,
      "168f0182fe0d6b70cbcd703e8231cb6ec9b00e48b82553d2268e863673db9d5d" },
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D3252, 0x005d3252u, 0x005d3268u, 22u,
      "7ce8ffee402aeb8feb8466c3c0e9a30fdf298da4d802b163177382ad2e68efd7" },
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D350C, 0x005d350cu, 0x005d351cu, 16u,
      "8ea6f391830530c2ad52d4854cdfc6756a0912f1a2be710e1243152fc4dc025f" },
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D351C, 0x005d351cu, 0x005d352eu, 18u,
      "9a093499e92e7287c8704215ebfd29314122a5c0fbf46382c28032d6c5ca50f1" },
    { OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D4ED0, 0x005d4ed0u, 0x005d6d98u, 7880u,
      "f511d49d334e960c2d714c529998d5de6d3663ddba6c84c5c73e17f3a48a6934" }
};

static enum open_cfw_cordio_ll_sea_status open_cfw_cordio_ll_sea_read32(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t address,
    uint32_t *value
)
{
    enum open_cfw_cordio_ll_sea_status status;

    if (reader == 0 || reader->read_u32 == 0 || value == 0) {
        return OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT;
    }
    status = reader->read_u32(reader->context, address, value);
    return status == OPEN_CFW_CORDIO_LL_SEA_OK
        ? OPEN_CFW_CORDIO_LL_SEA_OK
        : OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
}

const struct open_cfw_cordio_ll_sea_external_evidence *
open_cfw_cordio_ll_sea_external_evidence(
    enum open_cfw_cordio_ll_sea_external_id id
)
{
    if ((unsigned int)id >= OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_COUNT) {
        return 0;
    }
    return &open_cfw_cordio_ll_sea_external_spans[(unsigned int)id];
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_external_candidate(
    enum open_cfw_cordio_ll_sea_external_id id,
    open_cfw_cordio_ll_sea_external_provider_t provider,
    void *provider_context,
    const struct open_cfw_cordio_ll_sea_external_invocation *invocation
)
{
    enum open_cfw_cordio_ll_sea_status status;

    if (
        open_cfw_cordio_ll_sea_external_evidence(id) == 0 ||
        invocation == 0
    ) {
        return OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT;
    }
    if (provider == 0) {
        return OPEN_CFW_CORDIO_LL_SEA_UNSUPPORTED_EXTERNAL;
    }
    status = provider(provider_context, id, invocation);
    return status == OPEN_CFW_CORDIO_LL_SEA_OK
        ? OPEN_CFW_CORDIO_LL_SEA_OK
        : OPEN_CFW_CORDIO_LL_SEA_PROVIDER_FAILED;
}

void open_cfw_cordio_ll_sea_write_once_u32_candidate(
    uint32_t *slot,
    uint32_t value
)
{
    if (slot != 0 && *slot == 0u) {
        *slot = value;
    }
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_load_field_218_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
)
{
    return open_cfw_cordio_ll_sea_read32(reader, object + 0x218u, value);
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_load_field_214_plus_c28_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
)
{
    enum open_cfw_cordio_ll_sea_status status =
        open_cfw_cordio_ll_sea_read32(reader, object + 0x214u, value);

    if (status == OPEN_CFW_CORDIO_LL_SEA_OK) {
        *value += 0x0c28u;
    }
    return status;
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_halfword_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
)
{
    uint32_t first;
    uint32_t second;
    uint16_t halfword;

    if (reader == 0 || reader->read_u16 == 0 || value == 0) {
        return OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT;
    }
    if (open_cfw_cordio_ll_sea_read32(reader, object + 4u, &first) !=
        OPEN_CFW_CORDIO_LL_SEA_OK) {
        return OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
    }
    if (open_cfw_cordio_ll_sea_read32(reader, first + 0x58u, &second) !=
        OPEN_CFW_CORDIO_LL_SEA_OK) {
        return OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
    }
    if (reader->read_u16(reader->context, second + 0x0eu, &halfword) !=
        OPEN_CFW_CORDIO_LL_SEA_OK) {
        return OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
    }
    *value = (uint32_t)halfword << 16;
    return OPEN_CFW_CORDIO_LL_SEA_OK;
}

static enum open_cfw_cordio_ll_sea_status open_cfw_cordio_ll_sea_nested_word_q16(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t nested_offset,
    uint32_t *value
)
{
    uint32_t nested;

    if (value == 0) {
        return OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT;
    }
    if (open_cfw_cordio_ll_sea_read32(reader, object + 0x218u, &nested) !=
        OPEN_CFW_CORDIO_LL_SEA_OK) {
        return reader == 0 || reader->read_u32 == 0
            ? OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT
            : OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
    }
    if (open_cfw_cordio_ll_sea_read32(reader, nested + nested_offset, value) !=
        OPEN_CFW_CORDIO_LL_SEA_OK) {
        return OPEN_CFW_CORDIO_LL_SEA_READ_FAILED;
    }
    *value <<= 16;
    return OPEN_CFW_CORDIO_LL_SEA_OK;
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_word_190_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
)
{
    return open_cfw_cordio_ll_sea_nested_word_q16(reader, object, 0x190u, value);
}

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_word_18c_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
)
{
    return open_cfw_cordio_ll_sea_nested_word_q16(reader, object, 0x18cu, value);
}
