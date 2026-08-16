#ifndef OPENR1_RECONSTRUCTED_MODEL_DATA_H
#define OPENR1_RECONSTRUCTED_MODEL_DATA_H

/* Transparent source representation of the overlapping generated-model
 * region recovered from the R1 application.  The values are model
 * parameters and descriptor words, not executable instructions. */

#include <stddef.h>
#include <stdint.h>

#define R1_MODEL_DATA_STOCK_BASE UINT32_C(0x000B19E4)
#define R1_MODEL_DATA_WORD_COUNT 11581u

#define R1_GOODIX_MODEL_STOCK_BASE UINT32_C(0x000B19E4)
#define R1_GOODIX_MODEL_WORD_OFFSET 0u
#define R1_GOODIX_MODEL_WORD_COUNT 3924u

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
extern const r1_model_data_view r1_goodix_generated_model;
extern const r1_model_data_view r1_gomore_sleep_model_below_100;
extern const r1_model_data_view r1_gomore_sleep_model_100_and_above;

#endif
