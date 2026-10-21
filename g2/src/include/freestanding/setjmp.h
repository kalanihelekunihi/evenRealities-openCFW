#ifndef G2_FT_ANALYSIS_SETJMP_H
#define G2_FT_ANALYSIS_SETJMP_H
/* Native G2 gray_TWorker has the next field at offset 128; its setjmp
 * saves 104 bytes. This compile-only layout is source inference, not
 * a qualified production libc contract. */
typedef unsigned long jmp_buf[32];
int setjmp(jmp_buf);
void longjmp(jmp_buf, int);
#endif
