/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Clean-room primitives and unsupported-provider boundary for the closed
 * 890-byte EM9305 residual tail partition.
 */

#ifndef OPEN_CFW_RUNTIME_EM9305_UNCLASSIFIED_TAIL_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EM9305_UNCLASSIFIED_TAIL_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPEN_CFW_EM9305_TAIL_SPAN_COUNT 36u
#define OPEN_CFW_EM9305_TAIL_TOTAL_BYTES 890u
#define OPEN_CFW_EM9305_TAIL_RECONSTRUCTIBLE_SPANS 21u
#define OPEN_CFW_EM9305_TAIL_RECONSTRUCTIBLE_BYTES 260u
#define OPEN_CFW_EM9305_TAIL_EXTERNAL_SPANS 15u
#define OPEN_CFW_EM9305_TAIL_EXTERNAL_BYTES 630u

enum open_cfw_em9305_tail_status {
    OPEN_CFW_EM9305_TAIL_OK = 0,
    OPEN_CFW_EM9305_TAIL_INVALID_ARGUMENT = 1,
    OPEN_CFW_EM9305_TAIL_UNSUPPORTED_EXTERNAL = 2,
    OPEN_CFW_EM9305_TAIL_PROVIDER_FAILED = 3
};

enum open_cfw_em9305_tail_external_id {
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00307D64 = 0,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0030AE24 = 1,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0030B1AC = 2,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0030C094 = 3,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0030C228 = 4,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_003100EC = 5,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00314728 = 6,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00314754 = 7,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_003151CC = 8,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00318200 = 9,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0031A980 = 10,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_0031E8FC = 11,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_003228A8 = 12,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00324AA0 = 13,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_00332CC0 = 14,
    OPEN_CFW_EM9305_TAIL_EXTERNAL_COUNT = 15
};

struct open_cfw_em9305_tail_external_evidence {
    enum open_cfw_em9305_tail_external_id id;
    uintptr_t stock_start;
    uintptr_t stock_end_exclusive;
    size_t stock_bytes;
    const char *stock_sha256;
};

struct open_cfw_em9305_tail_external_invocation {
    uintptr_t words[4];
};

typedef enum open_cfw_em9305_tail_status
(*open_cfw_em9305_tail_external_provider_t)(
    void *context,
    enum open_cfw_em9305_tail_external_id id,
    const struct open_cfw_em9305_tail_external_invocation *invocation
);

const struct open_cfw_em9305_tail_external_evidence *
open_cfw_em9305_tail_external_evidence(
    enum open_cfw_em9305_tail_external_id id
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_external_candidate(
    enum open_cfw_em9305_tail_external_id id,
    open_cfw_em9305_tail_external_provider_t provider,
    void *provider_context,
    const struct open_cfw_em9305_tail_external_invocation *invocation
);

void open_cfw_em9305_tail_no_op_candidate(void);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u8_candidate(
    const volatile uint8_t *storage,
    uint8_t *value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u16_candidate(
    const volatile uint16_t *storage,
    uint16_t *value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u32_candidate(
    const volatile uint32_t *storage,
    uint32_t *value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u8_candidate(
    volatile uint8_t *storage,
    uint8_t value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u16_candidate(
    volatile uint16_t *storage,
    uint16_t value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u32_candidate(
    volatile uint32_t *storage,
    uint32_t value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_load_u8_at_candidate(
    const uint8_t *base,
    size_t offset,
    uint8_t *value
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_store_u8_at_candidate(
    uint8_t *base,
    size_t offset,
    uint8_t value
);

uint32_t open_cfw_em9305_tail_u8_nonzero_candidate(uint8_t value);
uint32_t open_cfw_em9305_tail_u8_equals_candidate(uint8_t value, uint8_t expected);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_set_bits32_candidate(
    volatile uint32_t *storage,
    uint32_t mask
);

enum open_cfw_em9305_tail_status open_cfw_em9305_tail_zero_memory_candidate(
    void *storage,
    size_t bytes
);

#ifdef __cplusplus
}
#endif

#endif
