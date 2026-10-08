/* Independently reconstructed stock signed/unsigned conversion cursor fragments.
 * 41ef8c..41eff2 and41f022..41f088; rendering remains separate. */
#include <stdint.h>
void opencfw_format_integer_fetch(uint32_t **cursor,unsigned length,unsigned signed_value,uint32_t out[2]){
 uint32_t *p=*cursor;uint32_t low,high;
 if(length=='j'||length=='q'){
  p=(uint32_t *)(((uintptr_t)p+7u)&~(uintptr_t)7u);low=p[0];high=p[1];p+=2;
 }else{
  low=*p++;
  if(length=='b')low=signed_value?(uint32_t)(int32_t)(int8_t)low:(uint8_t)low;
  else if(length=='h')low=signed_value?(uint32_t)(int32_t)(int16_t)low:(uint16_t)low;
  high=signed_value&&((int32_t)low<0)?UINT32_MAX:0;
 }
 *cursor=p;out[0]=low;out[1]=high;
}
