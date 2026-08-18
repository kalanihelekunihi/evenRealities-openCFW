#include <assert.h>
#include <string.h>

#include "model_data/r1_model_data.h"

void test_reconstructed_model_data(void) {
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_MODE_0_WORD_OFFSET] ==
           UINT32_C(0x3A97DFDD));
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_MODE_0_WORD_OFFSET +
               R1_GOODIX_HRV_MODE_0_WORD_COUNT - 1u] ==
           UINT32_C(0x3A97DFDD));
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_MODE_1_WORD_OFFSET] ==
           UINT32_C(0xBA8460F2));
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_MODE_2_WORD_OFFSET] ==
           UINT32_C(0x39010F70));
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_MODE_3_WORD_OFFSET] ==
           UINT32_C(0x38810F2D));
    assert(r1_goodix_hrv_weighted_words[
               R1_GOODIX_HRV_WEIGHTED_WORD_COUNT - 1u] ==
           UINT32_C(0x38810F2D));
    assert(r1_goodix_hrv_extrema_curve_words[0] ==
           UINT32_C(0x3F800000));
    assert(r1_goodix_hrv_extrema_curve_words[3] ==
           UINT32_C(0x40800000));
    assert(r1_goodix_hrv_extrema_curve_words[4] ==
           UINT32_C(0x3F800000));
    assert(r1_goodix_hrv_extrema_curve_words[7] ==
           UINT32_C(0x40800000));

    assert(r1_goodix_hba_family_1_graph.word_count == 2979u);
    assert(r1_goodix_hba_family_1_graph.stock_base_address ==
           UINT32_C(0x0009D640));
    assert(r1_goodix_hba_mode_0_descriptors.word_count == 4857u);
    assert(r1_goodix_hba_second_graph.word_count == 1567u);
    assert(r1_goodix_hba_family_0_graph.word_count == 6660u);
    assert(r1_goodix_hba_filter_coefficients.word_count == 20u);
    assert(r1_goodix_hba_filter_coefficients.words[0] ==
           UINT32_C(0x3EC74BD4));
    assert(r1_goodix_hba_filter_coefficients.words[1] == 0u);
    assert(r1_goodix_hba_filter_coefficients.words[4] ==
           UINT32_C(0xBF105C2E));
    assert(r1_goodix_hba_filter_coefficients.words[19] ==
           UINT32_C(0xBE3909B5));
    static const uint32_t expected_hba_configuration[
        R1_GOODIX_HBA_CONFIGURATION_WORD_COUNT] = {
        0u, 25u, 4u, 9u, 20u, 1u, 202u, 5u, 1u,
    };
    assert(memcmp(r1_goodix_hba_configuration_words,
                  expected_hba_configuration,
                  sizeof(expected_hba_configuration)) == 0);
    static const uint8_t expected_hba_tail_schema[
        R1_GOODIX_HBA_TAIL_SCHEMA_BYTE_COUNT] = {
        23u, 104u, 32u, 23u, 32u, 21u, 21u, 1u,
        16u, 56u, 16u, 16u, 16u, 16u, 16u, 1u,
        8u, 104u, 8u, 8u, 8u, 21u, 21u, 10u,
    };
    for (size_t index = 0u;
            index < R1_GOODIX_HBA_TAIL_SCHEMA_BYTE_COUNT; ++index) {
        assert(r1_goodix_hba_tail_schema[index] ==
               expected_hba_tail_schema[index]);
    }

    assert(r1_goodix_spo2_configuration[0] == UINT8_C(0x01));
    assert(r1_goodix_spo2_configuration[4] == UINT8_C(0x19));
    assert(r1_goodix_spo2_configuration[16] == UINT8_C(0x8A));
    assert(r1_goodix_spo2_configuration[28] == UINT8_C(0x01));
    assert(r1_goodix_spo2_configuration[73] == UINT8_C(0x0A));
    assert(r1_goodix_spo2_configuration[75] == UINT8_C(0x03));
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_0_WORD_OFFSET] == 100000);
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_0_WORD_OFFSET + 7u] == 2440000);
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_1_WORD_OFFSET] == 10000);
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_1_WORD_OFFSET + 12u] == 2000000);
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_2_WORD_OFFSET] == 7812);
    assert(r1_goodix_spo2_scale_words[
               R1_GOODIX_SPO2_SCALE_MODE_2_WORD_OFFSET + 8u] == 2000000);
    assert(r1_goodix_spo2_spectral_words[
               R1_GOODIX_SPO2_SPECTRAL_FACTOR_WORD_OFFSET] ==
           UINT32_C(0x3FC00000));
    assert(r1_goodix_spo2_spectral_words[
               R1_GOODIX_SPO2_SPECTRAL_SCALE_WORD_OFFSET] == 0u);
    assert(r1_goodix_spo2_spectral_words[
           R1_GOODIX_SPO2_SPECTRAL_WORD_COUNT - 1u] ==
           UINT32_C(0x3AA58B3F));

    assert(r1_goodix_generated_model.words == r1_model_data_words);
    assert(r1_goodix_generated_model.word_count == 3924u);
    assert(r1_goodix_generated_model.stock_base_address ==
           UINT32_C(0x000B19E4));
    assert(r1_goodix_generated_model.words[0] == UINT32_C(0x00000004));
    assert(r1_goodix_generated_model.words[3923] ==
           UINT32_C(0x15FB0D0F));

    assert(r1_gomore_sleep_model_below_100.words ==
           r1_model_data_words + 669u);
    assert(r1_gomore_sleep_model_below_100.word_count == 5456u);
    assert(r1_gomore_sleep_model_below_100.words[0] ==
           UINT32_C(0x36AFAF56));
    assert(r1_gomore_sleep_model_below_100.words[5455] ==
           UINT32_C(0xB10B3866));

    assert(r1_gomore_sleep_model_100_and_above.words ==
           r1_model_data_words + 6125u);
    assert(r1_gomore_sleep_model_100_and_above.word_count == 5456u);
    assert(r1_gomore_sleep_model_100_and_above.words[0] ==
           UINT32_C(0x3652B1C9));
    assert(r1_gomore_sleep_model_100_and_above.words[5455] ==
           UINT32_C(0xB2BC3968));
}
