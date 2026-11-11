#ifndef R1_GOODIX_NATIVE_NADT_PUBLIC_VIEW_H
#define R1_GOODIX_NATIVE_NADT_PUBLIC_VIEW_H

#include <stdbool.h>
#include "goodix_nadt.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"

extern const float r1_goodix_nadt_primary_boundary_coefficients[
    GOODIX_PRIMITIVES_NADT_PRIMARY_BOUNDARY_COEFFICIENTS];

/* Borrow the public sample buffers for the recovered 0x36034 preparation
 * helper, which writes three prepared lanes through ppg_rawdata. */
bool r1_goodix_nadt_public_sample_view(
    const goodix_nadt_input_rawdata *raw,
    goodix_primitives_nadt_sample_preparation_input *view);

/* The stock window classifier reads four statistic banks in the final
 * 68 bytes of the native workspace, followed immediately by the 120-byte
 * configuration. Load/store only the fields the typed stream owns. */
bool r1_goodix_nadt_window_configuration_load(
    const uint8_t tail[68], const volatile uint8_t configuration[120],
    goodix_primitives_nadt_window_configuration *view);
void r1_goodix_nadt_window_configuration_store(
    uint8_t tail[68],
    const goodix_primitives_nadt_window_configuration *view);

/* Project the 92-byte native state and four running-statistics banks without
 * copying the 1,588-byte native workspace. Unknown native bytes stay owned
 * by the initializer/reset implementation. */
bool r1_goodix_nadt_stream_state_load(
    const volatile uint8_t native_state[92], const uint8_t tail[68],
    goodix_primitives_nadt_stream_state *view);
void r1_goodix_nadt_stream_state_store(
    volatile uint8_t native_state[92], uint8_t tail[68],
    const goodix_primitives_nadt_stream_state *view);
void r1_goodix_nadt_preparation_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_sample_preparation_state *view);
void r1_goodix_nadt_preparation_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_sample_preparation_state *view);

bool r1_goodix_nadt_auxiliary_configuration_load(
    const volatile uint8_t configuration[120],
    goodix_primitives_nadt_auxiliary_configuration *view);
bool r1_goodix_nadt_alternate_configuration_load(
    const volatile uint8_t configuration[120],
    goodix_primitives_nadt_alternate_configuration *view);

/* The primary classifier reads threshold fields from the native 120-byte
 * configuration, and extrema banks from the preceding workspace tail.
 * Boundary coefficients are source-owned and supplied by the caller. */
bool r1_goodix_nadt_primary_configuration_load(
    const uint8_t tail[68], const volatile uint8_t configuration[120],
    const float *boundary_coefficients, size_t boundary_coefficient_count,
    goodix_primitives_nadt_primary_configuration *view);

/* Auxiliary classifier shares the native result word and mode byte with the
 * main classifier. Only its own consecutive counter is committed here. */
bool r1_goodix_nadt_auxiliary_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_auxiliary_state *view);
void r1_goodix_nadt_auxiliary_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_auxiliary_state *view);

bool r1_goodix_nadt_alternate_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_alternate_state *view);
void r1_goodix_nadt_alternate_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_alternate_state *view);

#endif
