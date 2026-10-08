/* Independent exact binary32 remainder reconstruction, stock427ccc/427cdc.
 * Integer operations avoid host libm and preserve sign/NaN/error behavior.
 * Pending original-instruction validation. */
#include <stdint.h>
float opencfw_boot_pll_mod(float,float) __attribute__((pcs("aapcs-vfp")));
typedef union {float f;uint32_t bits;} binary32;
float opencfw_boot_pll_mod(float first,float second){
 binary32 x={.f=first},y={.f=second};uint32_t sign=x.bits&0x80000000u;
 uint32_t ax=x.bits&0x7fffffffu,ay=y.bits&0x7fffffffu;
 /* Stock canonical NaN is all positive payload bits set. Only finite x
  * with zero divisor takes domain-store33; infinity/NaN x does not. */
 if(ax>=0x7f800000u||ay>0x7f800000u||ay==0){
  if(ax<0x7f800000u&&ay==0)*(volatile uint32_t *)(uintptr_t)0x20027194=33;
  x.bits=0x7fffffffu;return x.f;
 }
 if(ax<ay)return x.f;
 if(ax==ay){x.bits=sign;return x.f;}
 int ex=(int)(ax>>23),ey=(int)(ay>>23);
 uint32_t mx=ax&0x7fffffu,my=ay&0x7fffffu;
 if(ex)mx|=0x800000u;else{ex=1;while(!(mx&0x800000u)){mx<<=1;--ex;}}
 if(ey)my|=0x800000u;else{ey=1;while(!(my&0x800000u)){my<<=1;--ey;}}
 while(ex>ey){if(mx>=my)mx-=my;if(!mx){x.bits=sign;return x.f;}mx<<=1;--ex;}
 if(mx>=my)mx-=my;
 if(!mx){x.bits=sign;return x.f;}
 while(!(mx&0x800000u)){mx<<=1;--ex;}
 if(ex>0)x.bits=sign|((uint32_t)ex<<23)|(mx&0x7fffffu);
 else x.bits=sign|(mx>>(1-ex));
 return x.f;
}
