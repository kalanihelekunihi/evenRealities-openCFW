#ifndef OPENR1_RECONSTRUCTED_MODEL_DATA_H
#define OPENR1_RECONSTRUCTED_MODEL_DATA_H

/* Transparent source representation of the overlapping generated-model
 * region recovered from the R1 application.  The values are model
 * parameters and descriptor words, not executable instructions. */

#include <stddef.h>
#include <stdint.h>

#define R1_MODEL_DATA_STOCK_BASE UINT32_C(0x000B19E4)
#define R1_MODEL_DATA_WORD_COUNT 11581u

/* Exact GH_HRV/HR processing constants referenced by retail 0x00030368 and
 * 0x00034CBC.  The four weighted-feature banks are contiguous in the stock
 * image: modes 0..2 contain 65 Float32 words and mode 3 contains 129. */
#define R1_GOODIX_HRV_WEIGHTED_WORD_COUNT 324u
#define R1_GOODIX_HRV_MODE_0_WORD_OFFSET 0u
#define R1_GOODIX_HRV_MODE_1_WORD_OFFSET 65u
#define R1_GOODIX_HRV_MODE_2_WORD_OFFSET 130u
#define R1_GOODIX_HRV_MODE_3_WORD_OFFSET 195u
#define R1_GOODIX_HRV_MODE_0_WORD_COUNT 65u
#define R1_GOODIX_HRV_MODE_1_WORD_COUNT 65u
#define R1_GOODIX_HRV_MODE_2_WORD_COUNT 65u
#define R1_GOODIX_HRV_MODE_3_WORD_COUNT 129u
#define R1_GOODIX_HRV_EXTREMA_CURVE_WORD_COUNT 8u

/* Exact non-executable graph descriptors, quantized parameters, remap data,
 * and stream-filter coefficients consumed by the retail GH_HBA initializer
 * at 0x0006D204.  Unreferenced bytes between stock regions are omitted. */
#define R1_GOODIX_HBA_FAMILY_1_STOCK_BASE UINT32_C(0x0009D640)
#define R1_GOODIX_HBA_FAMILY_1_WORD_OFFSET 0u
#define R1_GOODIX_HBA_FAMILY_1_WORD_COUNT 2979u
#define R1_GOODIX_HBA_MODE_0_STOCK_BASE UINT32_C(0x000A04CC)
#define R1_GOODIX_HBA_MODE_0_WORD_OFFSET 2979u
#define R1_GOODIX_HBA_MODE_0_WORD_COUNT 4857u
#define R1_GOODIX_HBA_SECOND_STOCK_BASE UINT32_C(0x000A50B0)
#define R1_GOODIX_HBA_SECOND_WORD_OFFSET 7836u
#define R1_GOODIX_HBA_SECOND_WORD_COUNT 1567u
#define R1_GOODIX_HBA_FAMILY_0_STOCK_BASE UINT32_C(0x000A692C)
#define R1_GOODIX_HBA_FAMILY_0_WORD_OFFSET 9403u
#define R1_GOODIX_HBA_FAMILY_0_WORD_COUNT 6660u
#define R1_GOODIX_HBA_FILTER_STOCK_BASE UINT32_C(0x000B0F0C)
#define R1_GOODIX_HBA_FILTER_WORD_OFFSET 16063u
#define R1_GOODIX_HBA_FILTER_WORD_COUNT 20u
#define R1_GOODIX_HBA_WORD_COUNT 16083u

#define R1_GOODIX_HBA_CONFIGURATION_STOCK_BASE UINT32_C(0x000AD13C)
#define R1_GOODIX_HBA_CONFIGURATION_WORD_COUNT 9u

/* Per-mode {recurrent,dense} tail dimensions recovered from initialized RAM
 * at 0x20007D98.  Eight bytes belong to each executor mode. */
#define R1_GOODIX_HBA_TAIL_SCHEMA_MODE_COUNT 3u
#define R1_GOODIX_HBA_TAIL_SCHEMA_BYTES_PER_MODE 8u
#define R1_GOODIX_HBA_TAIL_SCHEMA_BYTE_COUNT 24u

#define R1_GOODIX_MODEL_STOCK_BASE UINT32_C(0x000B19E4)
#define R1_GOODIX_MODEL_WORD_OFFSET 0u
#define R1_GOODIX_MODEL_WORD_COUNT 3924u

#define R1_GOODIX_SPO2_CONFIGURATION_STOCK_BASE UINT32_C(0x000AD160)
#define R1_GOODIX_SPO2_CONFIGURATION_BYTE_COUNT 76u

/* Exact initialized-RAM scale tables consumed by retail 0x000335B4.  The
 * startup decompressor at 0x000286F4 materializes these from the application
 * load image; the reconstruction stores the resulting integers directly. */
#define R1_GOODIX_SPO2_SCALE_MODE_0_WORD_OFFSET 0u
#define R1_GOODIX_SPO2_SCALE_MODE_0_WORD_COUNT 8u
#define R1_GOODIX_SPO2_SCALE_MODE_1_WORD_OFFSET 8u
#define R1_GOODIX_SPO2_SCALE_MODE_1_WORD_COUNT 13u
#define R1_GOODIX_SPO2_SCALE_MODE_2_WORD_OFFSET 21u
#define R1_GOODIX_SPO2_SCALE_MODE_2_WORD_COUNT 9u
#define R1_GOODIX_SPO2_SCALE_WORD_COUNT 30u

/* Exact Float32 factor plus 125 mode-one channel-scale words loaded through
 * the literal bindings at 0x00032780/0x00032784 by retail 0x00032744. */
#define R1_GOODIX_SPO2_SPECTRAL_FACTOR_WORD_OFFSET 0u
#define R1_GOODIX_SPO2_SPECTRAL_SCALE_WORD_OFFSET 1u
#define R1_GOODIX_SPO2_SPECTRAL_SCALE_WORD_COUNT 125u
#define R1_GOODIX_SPO2_SPECTRAL_WORD_COUNT 126u

#define R1_GOMORE_SLEEP_BELOW_100_STOCK_BASE UINT32_C(0x000B2458)
#define R1_GOMORE_SLEEP_BELOW_100_WORD_OFFSET 669u
#define R1_GOMORE_SLEEP_BELOW_100_WORD_COUNT 5456u

#define R1_GOMORE_SLEEP_100_AND_ABOVE_STOCK_BASE UINT32_C(0x000B7998)
#define R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_OFFSET 6125u
#define R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_COUNT 5456u

typedef struct {
    const uint32_t *words;
    size_t word_count;
    uint32_t stock_base_address;
} r1_model_data_view;

extern const uint32_t r1_model_data_words[R1_MODEL_DATA_WORD_COUNT];
extern const uint32_t r1_goodix_hrv_weighted_words[
    R1_GOODIX_HRV_WEIGHTED_WORD_COUNT];
extern const uint32_t r1_goodix_hrv_extrema_curve_words[
    R1_GOODIX_HRV_EXTREMA_CURVE_WORD_COUNT];
extern const uint32_t r1_goodix_hba_words[R1_GOODIX_HBA_WORD_COUNT];
extern const uint32_t r1_goodix_hba_configuration_words[
    R1_GOODIX_HBA_CONFIGURATION_WORD_COUNT];
extern const uint8_t r1_goodix_hba_tail_schema[
    R1_GOODIX_HBA_TAIL_SCHEMA_BYTE_COUNT];
extern const uint8_t r1_goodix_spo2_configuration[
    R1_GOODIX_SPO2_CONFIGURATION_BYTE_COUNT];
extern const int32_t r1_goodix_spo2_scale_words[
    R1_GOODIX_SPO2_SCALE_WORD_COUNT];
extern const uint32_t r1_goodix_spo2_spectral_words[
    R1_GOODIX_SPO2_SPECTRAL_WORD_COUNT];
extern const r1_model_data_view r1_goodix_hba_family_1_graph;
extern const r1_model_data_view r1_goodix_hba_mode_0_descriptors;
extern const r1_model_data_view r1_goodix_hba_second_graph;
extern const r1_model_data_view r1_goodix_hba_family_0_graph;
extern const r1_model_data_view r1_goodix_hba_filter_coefficients;
extern const r1_model_data_view r1_goodix_generated_model;
extern const r1_model_data_view r1_gomore_sleep_model_below_100;
extern const r1_model_data_view r1_gomore_sleep_model_100_and_above;

#endif
