#include <stdint.h>
static uint32_t word(uintptr_t p,uint32_t offset){return *(const volatile uint32_t *)(p+offset);}
/* Native0x35d12. Selector bytes1/2 must index the three native strides.
 * Batch and selector byte0 are intentionally unused. Copy forward and live. */
uint32_t r1_goodix_native_graph_transform(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,in=word((uintptr_t)inputs,0),out=word((uintptr_t)outputs,0);
 uint32_t rows=word(in,8),columns=word(in,12),out_rows=word(out,8),out_columns=word(out,12);
 uint32_t strides[3]={columns*rows,columns,1};
 uint32_t a=*(const volatile uint8_t *)(op+1),b=*(const volatile uint8_t *)(op+2);
 uintptr_t source=word(in,16);uint32_t row_stride=strides[a];uintptr_t target=word(out,16);uint32_t column_stride=strides[b];
 for(uint32_t row=0;(int32_t)row<(int32_t)out_rows;++row)
  for(uint32_t column=0;(int32_t)column<(int32_t)out_columns;++column){
   uint32_t value=word(source,(column*column_stride+row*row_stride)*4u);
   *(volatile uint32_t *)(target+(row*out_columns+column)*4u)=value;
  }
 return 0;
}
const uint32_t r1_goodix_graph_transform_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_transform;
