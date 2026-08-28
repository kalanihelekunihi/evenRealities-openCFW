/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_KWS_MODEL_BOUNDARY_H
#define OPEN_CFW_GX8002_KWS_MODEL_BOUNDARY_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_GX8002_KWS_WEIGHT_SIZE ((size_t)120800U)
#define OPEN_CFW_GX8002_KWS_WEIGHT_SHA256_HEX \
    "397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf"

enum {
    OPEN_CFW_GX8002_MODEL_OK = 0,
    OPEN_CFW_GX8002_MODEL_INVALID = 1,
    OPEN_CFW_GX8002_MODEL_UNSUPPORTED = 2,
    OPEN_CFW_GX8002_MODEL_PROVIDER_FAILED = 3,
    OPEN_CFW_GX8002_MODEL_IDENTITY_MISMATCH = 4
};

/*
 * The provider owns source acquisition and redistribution authorization.
 * It must write only to destination[0..capacity) and set bytes_written.
 * This boundary independently verifies the exact G2 2.2.6.10 model identity.
 */
typedef int32_t (*open_cfw_gx8002_kws_model_provider_fn)(
    void *context,
    uint8_t *destination,
    size_t capacity,
    size_t *bytes_written);

typedef struct open_cfw_gx8002_kws_model_ports {
    void *context;
    open_cfw_gx8002_kws_model_provider_fn provider;
} open_cfw_gx8002_kws_model_ports;

typedef open_cfw_gx8002_kws_model_provider_fn open_cfw_gx8002_segment_provider_fn;
typedef open_cfw_gx8002_kws_model_ports open_cfw_gx8002_segment_ports;

/* Shared exact-segment verifier. expected_sha256 points to exactly 32 bytes. */
int32_t open_cfw_gx8002_authenticated_segment_load(
    const open_cfw_gx8002_segment_ports *ports,
    uint8_t *destination,
    size_t capacity,
    size_t expected_size,
    const uint8_t expected_sha256[32]);

int32_t open_cfw_gx8002_kws_model_load(
    const open_cfw_gx8002_kws_model_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
