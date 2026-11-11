#ifndef R1_NATIVE_SPO2_INFER_H
#define R1_NATIVE_SPO2_INFER_H
#include <stdint.h>
/* Native 0x968c4 interface used by goodix_spo2_calc. The second argument is
 * passed through by that caller but unused by this stock entry. */
uint32_t r1_goodix_spo2_infer(void *context_reference,const void *unused,void *model_descriptor,void *output,void *flags_reference);
#endif
