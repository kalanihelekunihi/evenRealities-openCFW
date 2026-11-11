/* Stock 0x684b4: copy an eleven-byte GoMore mode record from the
 * already source-owned non-executable model-data region. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"
#include "../../vendor/model_data/r1_model_data.h"

enum {
    R1_GOMORE_RECORD11_TABLE_OFFSET =
        UINT32_C(0x000B1BDE) - R1_MODEL_DATA_STOCK_BASE,
    R1_GOMORE_RECORD11_REACHABLE_BYTES = 1760u,
};

_Static_assert(R1_GOMORE_RECORD11_TABLE_OFFSET +
                   R1_GOMORE_RECORD11_REACHABLE_BYTES <=
                   sizeof(r1_model_data_words),
               "GoMore mode records must fit the source-owned model region");

void r1_gomore_table_record11_native(volatile void *output, uint32_t index)
{
    const uint8_t *table = (const uint8_t *)r1_model_data_words +
                           R1_GOMORE_RECORD11_TABLE_OFFSET;
    uint8_t record[11];
    if (gomore_primitives_table_record11(
            table, sizeof(r1_model_data_words) -
                       R1_GOMORE_RECORD11_TABLE_OFFSET,
            (int32_t)index, record)) {
        volatile uint8_t *destination = output;
        for (unsigned byte = 0u; byte < sizeof(record); ++byte) {
            destination[byte] = record[byte];
        }
    }
}
