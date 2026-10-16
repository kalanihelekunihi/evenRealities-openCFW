/* Arm EABI boolean comparisons for the pinned LLVM binary64 provider.
 * These are candidate ABI adapters, not recovered stock instruction identity.
 * LLVM __ledf2 returns +1 on unordered; __gedf2 returns -1 on unordered.
 * Their declarations use the build's hard-float PCS; EABI entries use core
 * registers. Keep the two interfaces explicit to prevent varargs corruption. */
extern int __ledf2(double, double);
extern int __gedf2(double, double);
#define EABI __attribute__((pcs("aapcs")))
EABI int __aeabi_dcmpeq(double a, double b) { return __ledf2(a,b)==0; }
EABI int __aeabi_dcmplt(double a, double b) { return __ledf2(a,b)<0; }
EABI int __aeabi_dcmple(double a, double b) { return __ledf2(a,b)<=0; }
EABI int __aeabi_dcmpgt(double a, double b) { return __gedf2(a,b)>0; }
