#ifndef R1_GOODIX_NATIVE_HBA_PUBLIC_VIEW_H
#define R1_GOODIX_NATIVE_HBA_PUBLIC_VIEW_H

#include <stdbool.h>
#include "goodix_hba.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"

/* Borrow the public buffers for one calculation. Neither view owns memory. */
bool r1_goodix_hba_public_input_view(
    const goodix_hba_input_rawdata *raw,
    goodix_primitives_hba_process_input *view);
void r1_goodix_hba_public_result_load(
    const goodix_hba_result *result,
    goodix_primitives_hba_process_output *output);
void r1_goodix_hba_public_result_store(
    const goodix_primitives_hba_process_output *output,
    goodix_hba_result *result);

#endif
