#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
uint32_t r1_goodix_native_tensor_concatenate(const void *operation,const void *inputs,const void *outputs,uint32_t operands)
{
 (void)operation;uintptr_t ins=(uintptr_t)inputs,outs=(uintptr_t)outputs;
 uint32_t batches=W(W(outs,0),4),columns=W(W(ins,0),12);uintptr_t target=W(W(outs,0),16);
 for(uint32_t batch=0;(int32_t)batch<(int32_t)batches;++batch){
  for(uint32_t input=0;(int32_t)input<(int32_t)operands;++input){
   uintptr_t descriptor=W(ins,input*4u);uint32_t rows=W(descriptor,8);uintptr_t source=W(descriptor,16);uint32_t words=columns*rows;
   (void)memmove((void *)target,(const void *)(source+(batch*words)*4u),words*4u);target+=words*4u;
  }
 }
 return 0;
}
uint32_t r1_goodix_native_model_concatenate(const void *operation,const void *inputs,const void *outputs)
{return r1_goodix_native_tensor_concatenate(operation,inputs,outputs,2);}
const uint32_t r1_goodix_model_vector_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_model_concatenate;
