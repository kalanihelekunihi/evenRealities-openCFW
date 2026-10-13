#include <stdint.h>
extern int __gedf2(double,double);
extern int __ledf2(double,double);
extern int __eqdf2(double,double);
int __aeabi_dcmpge(double a,double b){return __gedf2(a,b)>=0;}
int __aeabi_dcmpgt(double a,double b){return __gedf2(a,b)>0;}
int __aeabi_dcmple(double a,double b){return __ledf2(a,b)<=0;}
int __aeabi_dcmplt(double a,double b){return __ledf2(a,b)<0;}
int __aeabi_dcmpeq(double a,double b){return __eqdf2(a,b)==0;}
__attribute__((naked)) void __aeabi_uldivmod(void){__asm__ volatile(
 "push {r4,lr}\nsub sp,sp,#16\nadd r4,sp,#8\nstr r4,[sp]\nbl __udivmoddi4\nldr r2,[sp,#8]\nldr r3,[sp,#12]\nadd sp,sp,#16\npop {r4,pc}\n");}
