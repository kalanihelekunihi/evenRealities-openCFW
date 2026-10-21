#include "model_data/r1_model_data.h"

_Static_assert(
    R1_GOMORE_SLEEP_BELOW_100_WORD_OFFSET +
        R1_GOMORE_SLEEP_BELOW_100_WORD_COUNT <= R1_MODEL_DATA_WORD_COUNT,
    "below-100 sleep model must remain inside the recovered model region");
_Static_assert(
    R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_OFFSET +
        R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_COUNT == R1_MODEL_DATA_WORD_COUNT,
    "upper sleep model must end at the recovered model-region boundary");
_Static_assert(
    R1_GOODIX_MODEL_WORD_OFFSET + R1_GOODIX_MODEL_WORD_COUNT <=
        R1_MODEL_DATA_WORD_COUNT,
    "Goodix generated model must remain inside the recovered model region");

/* Generated as explicit integer constants by tools/generate_r1_model_data.py.
 * The build never reads or links the research firmware image. */
const uint32_t r1_model_data_words[R1_MODEL_DATA_WORD_COUNT] = {
#include "model_data/r1_model_data_generated.inc"
};

const uint32_t r1_goodix_hrv_weighted_words[
    R1_GOODIX_HRV_WEIGHTED_WORD_COUNT] = {
#include "model_data/r1_goodix_hrv_weighted_generated.inc"
};

const uint32_t r1_goodix_hrv_extrema_curve_words[
    R1_GOODIX_HRV_EXTREMA_CURVE_WORD_COUNT] = {
    UINT32_C(0x3F800000), UINT32_C(0x40000000),
    UINT32_C(0x40400000), UINT32_C(0x40800000),
    UINT32_C(0x3F800000), UINT32_C(0x40000000),
    UINT32_C(0x40400000), UINT32_C(0x40800000),
};

const uint32_t r1_goodix_hba_words[R1_GOODIX_HBA_WORD_COUNT] = {
#include "model_data/r1_goodix_hba_generated.inc"
};

const uint32_t r1_goodix_hba_configuration_words[
    R1_GOODIX_HBA_CONFIGURATION_WORD_COUNT] = {
#include "model_data/r1_goodix_hba_configuration_generated.inc"
};

const uint8_t r1_goodix_hba_tail_schema[
    R1_GOODIX_HBA_TAIL_SCHEMA_BYTE_COUNT] = {
#include "model_data/r1_goodix_hba_schema_generated.inc"
};

const uint8_t r1_goodix_spo2_configuration[
    R1_GOODIX_SPO2_CONFIGURATION_BYTE_COUNT] = {
#include "model_data/r1_goodix_spo2_configuration_generated.inc"
};

const int32_t r1_goodix_spo2_scale_words[
    R1_GOODIX_SPO2_SCALE_WORD_COUNT] = {
#include "model_data/r1_goodix_spo2_scale_generated.inc"
};

const uint32_t r1_goodix_spo2_spectral_words[
    R1_GOODIX_SPO2_SPECTRAL_WORD_COUNT] = {
#include "model_data/r1_goodix_spo2_spectral_generated.inc"
};

#define R1_HBA_VIEW(name, prefix)                                         \
    const r1_model_data_view name = {                                    \
        r1_goodix_hba_words + prefix##_WORD_OFFSET,                      \
        prefix##_WORD_COUNT, prefix##_STOCK_BASE,                        \
    }

R1_HBA_VIEW(r1_goodix_hba_family_1_graph, R1_GOODIX_HBA_FAMILY_1);
R1_HBA_VIEW(r1_goodix_hba_mode_0_descriptors, R1_GOODIX_HBA_MODE_0);
R1_HBA_VIEW(r1_goodix_hba_second_graph, R1_GOODIX_HBA_SECOND);
R1_HBA_VIEW(r1_goodix_hba_family_0_graph, R1_GOODIX_HBA_FAMILY_0);
R1_HBA_VIEW(r1_goodix_hba_filter_coefficients, R1_GOODIX_HBA_FILTER);

#undef R1_HBA_VIEW

const r1_model_data_view r1_goodix_generated_model = {
    r1_model_data_words + R1_GOODIX_MODEL_WORD_OFFSET,
    R1_GOODIX_MODEL_WORD_COUNT,
    R1_GOODIX_MODEL_STOCK_BASE,
};

const r1_model_data_view r1_gomore_sleep_model_below_100 = {
    r1_model_data_words + R1_GOMORE_SLEEP_BELOW_100_WORD_OFFSET,
    R1_GOMORE_SLEEP_BELOW_100_WORD_COUNT,
    R1_GOMORE_SLEEP_BELOW_100_STOCK_BASE,
};

const r1_model_data_view r1_gomore_sleep_model_100_and_above = {
    r1_model_data_words + R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_OFFSET,
    R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_COUNT,
    R1_GOMORE_SLEEP_100_AND_ABOVE_STOCK_BASE,
};
