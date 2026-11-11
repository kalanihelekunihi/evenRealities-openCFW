#ifndef R1_NATIVE_MODEL_GRAPH_EXECUTE_H
#define R1_NATIVE_MODEL_GRAPH_EXECUTE_H
#include <stdint.h>
/* Native descriptor-pointer ABI. These entries do not implement the older
 * portable bool/scratch APIs in goodix_primitives. */
uint32_t r1_goodix_native_model_u8_pipeline(const void *model,const void *inputs,void *outputs,const void *configuration);
uint32_t r1_goodix_native_model_float_projection(const void *model,void *input_descriptor,void *outputs,const void *configuration);
uint32_t r1_goodix_native_model_subgraph_execute(const void *model,void *workspace,void *destination);
uint32_t r1_goodix_native_model_graph_execute(const void *model,const void *unused,const void *input_buffers,const void *unused2,void *output_buffers,uint32_t unused3,uint32_t reset);
uint32_t r1_goodix_native_model_graph_execute_veneer(const void *model,const void *unused,const void *input_buffers,const void *unused2,void *output_buffers,uint32_t unused3,uint32_t reset);
#endif
