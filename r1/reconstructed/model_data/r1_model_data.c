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
