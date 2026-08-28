/*
 * SPDX-License-Identifier: Apache-2.0
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Bounded semantic candidates for the medium-confidence Apollo 0x5Dxxxx
 * Cordio/LL-island census.  Names describe observed behavior, not recovered
 * proprietary controller symbols.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_LL_SEA_BOUNDED_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_LL_SEA_BOUNDED_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPEN_CFW_CORDIO_LL_SEA_MEDIUM_FUNCTIONS 12u
#define OPEN_CFW_CORDIO_LL_SEA_MEDIUM_BYTES 9420u
#define OPEN_CFW_CORDIO_LL_SEA_CONCRETE_FUNCTIONS 6u
#define OPEN_CFW_CORDIO_LL_SEA_CONCRETE_BYTES 64u
#define OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_FUNCTIONS 6u
#define OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_BYTES 9356u

enum open_cfw_cordio_ll_sea_status {
    OPEN_CFW_CORDIO_LL_SEA_OK = 0,
    OPEN_CFW_CORDIO_LL_SEA_INVALID_ARGUMENT = 1,
    OPEN_CFW_CORDIO_LL_SEA_READ_FAILED = 2,
    OPEN_CFW_CORDIO_LL_SEA_UNSUPPORTED_EXTERNAL = 3,
    OPEN_CFW_CORDIO_LL_SEA_PROVIDER_FAILED = 4
};

typedef enum open_cfw_cordio_ll_sea_status
(*open_cfw_cordio_ll_sea_read_u16_t)(
    void *context,
    uint32_t address,
    uint16_t *value
);

typedef enum open_cfw_cordio_ll_sea_status
(*open_cfw_cordio_ll_sea_read_u32_t)(
    void *context,
    uint32_t address,
    uint32_t *value
);

struct open_cfw_cordio_ll_sea_reader {
    void *context;
    open_cfw_cordio_ll_sea_read_u16_t read_u16;
    open_cfw_cordio_ll_sea_read_u32_t read_u32;
};

enum open_cfw_cordio_ll_sea_external_id {
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D2418 = 0,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D2A18 = 1,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D3252 = 2,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D350C = 3,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D351C = 4,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_005D4ED0 = 5,
    OPEN_CFW_CORDIO_LL_SEA_EXTERNAL_COUNT = 6
};

struct open_cfw_cordio_ll_sea_external_evidence {
    enum open_cfw_cordio_ll_sea_external_id id;
    uint32_t stock_start;
    uint32_t stock_end_exclusive;
    size_t stock_bytes;
    const char *stock_sha256;
};

struct open_cfw_cordio_ll_sea_external_invocation {
    uintptr_t words[8];
};

typedef enum open_cfw_cordio_ll_sea_status
(*open_cfw_cordio_ll_sea_external_provider_t)(
    void *context,
    enum open_cfw_cordio_ll_sea_external_id id,
    const struct open_cfw_cordio_ll_sea_external_invocation *invocation
);

const struct open_cfw_cordio_ll_sea_external_evidence *
open_cfw_cordio_ll_sea_external_evidence(
    enum open_cfw_cordio_ll_sea_external_id id
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_external_candidate(
    enum open_cfw_cordio_ll_sea_external_id id,
    open_cfw_cordio_ll_sea_external_provider_t provider,
    void *provider_context,
    const struct open_cfw_cordio_ll_sea_external_invocation *invocation
);

void open_cfw_cordio_ll_sea_write_once_u32_candidate(
    uint32_t *slot,
    uint32_t value
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_load_field_218_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_load_field_214_plus_c28_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_halfword_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_word_190_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
);

enum open_cfw_cordio_ll_sea_status
open_cfw_cordio_ll_sea_nested_word_18c_q16_candidate(
    const struct open_cfw_cordio_ll_sea_reader *reader,
    uint32_t object,
    uint32_t *value
);

#ifdef __cplusplus
}
#endif

#endif
