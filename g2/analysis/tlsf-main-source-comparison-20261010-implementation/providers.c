#include <stddef.h>
void *memcpy(void *d,const void *s,size_t n){unsigned char *a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}
void __assert_func(const char*f,int line,const char*fn,const char*expr){__asm__ volatile("bkpt #1");for(;;){}}
int printf(const char *s,...){__asm__ volatile("bkpt #2");return 0;}
