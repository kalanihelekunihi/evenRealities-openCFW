#include <assert.h>

#include "model_data/r1_model_data.h"

void test_reconstructed_model_data(void) {
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
