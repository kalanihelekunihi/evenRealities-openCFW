#include <stddef.h>
/* Fixture contract: diagnostics terminate at BKPT 0xAB; no formatter/return. */
__attribute__((noreturn)) static void diagnostic_trap(void){__asm__ volatile("bkpt #0xab");__builtin_unreachable();}
__attribute__((noreturn)) void __assert_func(const char *file,int line,const char *function,const char *expression){diagnostic_trap();}
int printf(const char *format,...){diagnostic_trap();}
void *memcpy(void *destination,const void *source,size_t count){unsigned char *d=destination;const unsigned char*s=source;for(size_t i=0;i<count;i++)d[i]=s[i];return destination;}
