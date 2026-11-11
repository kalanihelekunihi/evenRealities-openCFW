#ifndef R1_NATIVE_SPO2_INFER_SUPPORT_H
#define R1_NATIVE_SPO2_INFER_SUPPORT_H
#include <stdint.h>
void r1_goodix_native_spo2_clip_normalize(const void *input,uint32_t count,void *output);
void *r1_goodix_native_tensor_descriptor_initialize(void *descriptor,uint32_t batches,uint32_t rows,uint32_t columns,uint32_t element_bytes,void *data);
#endif
