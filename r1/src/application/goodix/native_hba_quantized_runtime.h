#ifndef R1_GOODIX_HBA_QUANTIZED_RUNTIME_H
#define R1_GOODIX_HBA_QUANTIZED_RUNTIME_H

#include "../../vendor/quantized_runtime/quantized_runtime.h"

/* Bind the source-owned numeric and sort providers used by HBA graphs.
 * The target's GoMore-only slice and scaled-multiply seams remain unbound. */
void r1_goodix_hba_quantized_runtime_initialize(quantized_runtime *runtime);

#endif
