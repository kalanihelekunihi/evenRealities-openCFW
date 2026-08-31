/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Original OpenCFW semantic primitives.  Absolute stock RAM/MMIO addresses
 * are deliberately supplied by a future reviewed binding, never embedded in
 * these host-testable candidates.
 */

#include "runtime_unclassified_tail_candidate.h"

static const struct open_cfw_em9305_tail_external_evidence
open_cfw_em9305_tail_external_spans[OPEN_CFW_EM9305_TAIL_EXTERNAL_COUNT] = {
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00307D64, 0x00307d64u, 0x00307d74u, 16u,
      "38561fc529c82682baff0731b072f5c8ece675e2dbbac44907e0eae4b41e4aee" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0030AE24, 0x0030ae24u, 0x0030ae8eu, 106u,
      "111cabb51a8da4d4b6e93bb3895ea2589a65928d1f4145f5268c1b8468a71bcf" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0030B1AC, 0x0030b1acu, 0x0030b1b0u, 4u,
      "524e4a6d405502d302a5d2914a638afd64fd710faf195d94cb9513cff832cf55" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0030C094, 0x0030c094u, 0x0030c098u, 4u,
      "ae3c1ff0998a3dd9cdc6edaccc1ca37e82a806821e9672e970522c0739ac0b51" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0030C228, 0x0030c228u, 0x0030c2bau, 146u,
      "3d156d34ec0a71749184874e8e7b4e1d292c4f40a54f276c584423da04b2d3c8" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_003100EC, 0x003100ecu, 0x003100f0u, 4u,
      "f64115f823d5675ed59321d1edd7c76faddd893e7ed7914dec00cb156a6a8a04" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00314728, 0x00314728u, 0x0031472cu, 4u,
      "76480290f1bed14bc2e72564d8cd92c60c121828769377b8e273db70826ccd34" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00314754, 0x00314754u, 0x00314758u, 4u,
      "656dbbb016eb58584b3cb5ce6b5ef6ac18bfcddbc473659e52b315a8acf4d563" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_003151CC, 0x003151ccu, 0x003151d4u, 8u,
      "15d7c55bcc02adb136a0a09e5faa4d0a06c22fbf9973583eef927924cb300f0b" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00318200, 0x00318200u, 0x0031825au, 90u,
      "9a49d807290a40e9bba88c523763357be2220f0f95900d0209e1bb000dceb1b6" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0031A980, 0x0031a980u, 0x0031a986u, 6u,
      "2bc255232d64dcd49926b2b18c42f157dff8aa7885cb8108394cbd8a6426b7a4" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_0031E8FC, 0x0031e8fcu, 0x0031e93eu, 66u,
      "71d7d7e4bc037887bf7709e9ad44071bb4201ae3c3c8dac93d563e428e97ce36" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_003228A8, 0x003228a8u, 0x003228e2u, 58u,
      "456db8aafcf0964daefa5eb57f320bfd18fb47ef039eca3ffa30e61dd052298b" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00324AA0, 0x00324aa0u, 0x00324aa8u, 8u,
      "f46359ecc7aa1dce7c9df5725c518e7b0831a8b91104bda02a57225406775613" },
    { OPEN_CFW_EM9305_TAIL_EXTERNAL_00332CC0, 0x00332cc0u, 0x00332d2au, 106u,
      "278b6770d19d7768fdf7a3e399aba046127b8a6ddc9f2ee0822dfdc1fb5ee4a5" }
};

static const struct open_cfw_em9305_tail_external_evidence *const
open_cfw_em9305_tail_external_spans_by_id[OPEN_CFW_EM9305_TAIL_EXTERNAL_COUNT] = {
    &open_cfw_em9305_tail_external_spans[0],
    &open_cfw_em9305_tail_external_spans[1],
    &open_cfw_em9305_tail_external_spans[2],
    &open_cfw_em9305_tail_external_spans[3],
    &open_cfw_em9305_tail_external_spans[4],
    &open_cfw_em9305_tail_external_spans[5],
    &open_cfw_em9305_tail_external_spans[6],
    &open_cfw_em9305_tail_external_spans[7],
    &open_cfw_em9305_tail_external_spans[8],
    &open_cfw_em9305_tail_external_spans[9],
    &open_cfw_em9305_tail_external_spans[10],
    &open_cfw_em9305_tail_external_spans[11],
    &open_cfw_em9305_tail_external_spans[12],
    &open_cfw_em9305_tail_external_spans[13],
    &open_cfw_em9305_tail_external_spans[14]
};

const struct open_cfw_em9305_tail_external_evidence *
open_cfw_em9305_tail_external_evidence(
    enum open_cfw_em9305_tail_external_id id
)
{
    if ((unsigned int)id >= OPEN_CFW_EM9305_TAIL_EXTERNAL_COUNT) {
        return 0;
    }
    return open_cfw_em9305_tail_external_spans_by_id[(unsigned int)id];
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_external_candidate(
    enum open_cfw_em9305_tail_external_id id,
    open_cfw_em9305_tail_external_provider_t provider,
    void *provider_context,
    const struct open_cfw_em9305_tail_external_invocation *invocation
)
{
    enum open_cfw_em9305_tail_status status;

    if (
        open_cfw_em9305_tail_external_evidence(id) == 0 ||
        invocation == 0
    ) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    if (provider == 0) {
        return OPEN_CFW_EM9305_TAIL_UNSUPPORTED_EXTERNAL;
    }
    status = provider(provider_context, id, invocation);
    return status == OPEN_CFW_EM9305_TAIL_OK
        ? OPEN_CFW_EM9305_TAIL_OK
        : OPEN_CFW_EM9305_TAIL_PROVIDER_FAILED;
}

void open_cfw_em9305_tail_no_op_candidate(void)
{
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u8_candidate(
    const volatile uint8_t *storage,
    uint8_t *value
)
{
    if (storage == 0 || value == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *value = *storage;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u16_candidate(
    const volatile uint16_t *storage,
    uint16_t *value
)
{
    if (storage == 0 || value == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *value = *storage;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u32_candidate(
    const volatile uint32_t *storage,
    uint32_t *value
)
{
    if (storage == 0 || value == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *value = *storage;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u8_candidate(
    volatile uint8_t *storage,
    uint8_t value
)
{
    if (storage == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *storage = value;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u16_candidate(
    volatile uint16_t *storage,
    uint16_t value
)
{
    if (storage == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *storage = value;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u32_candidate(
    volatile uint32_t *storage,
    uint32_t value
)
{
    if (storage == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *storage = value;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u8_at_candidate(
    const uint8_t *base,
    size_t offset,
    uint8_t *value
)
{
    if (base == 0 || value == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *value = base[offset];
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u8_at_candidate(
    uint8_t *base,
    size_t offset,
    uint8_t value
)
{
    if (base == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    base[offset] = value;
    return OPEN_CFW_EM9305_TAIL_OK;
}

uint32_t open_cfw_em9305_tail_u8_nonzero_candidate(uint8_t value)
{
    return value != 0u ? 1u : 0u;
}

uint32_t open_cfw_em9305_tail_u8_equals_candidate(
    uint8_t value,
    uint8_t expected
)
{
    return value == expected ? 1u : 0u;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_set_bits32_candidate(
    volatile uint32_t *storage,
    uint32_t mask
)
{
    if (storage == 0) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    *storage |= mask;
    return OPEN_CFW_EM9305_TAIL_OK;
}

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_zero_memory_candidate(
    void *storage,
    size_t bytes
)
{
    uint8_t *output = (uint8_t *)storage;
    size_t index;

    if (storage == 0 && bytes != 0u) {
        return OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT;
    }
    for (index = 0u; index < bytes; ++index) {
        output[index] = 0u;
    }
    return OPEN_CFW_EM9305_TAIL_OK;
}
