#include <stdint.h>
extern int __fe_getround(void);
extern int __fe_raise_inexact(void);
int main(void)
{
    uint32_t saved_fcr;
    __asm__ volatile("mfcr %0, cr<1, 2>" : "=a"(saved_fcr));
    static const int expected[4]={0,3,2,1};
    for (uint32_t c=0;c<4;c++) {
        uint32_t fcr=(saved_fcr&~(3u<<24))|(c<<24);
        __asm__ volatile("mtcr %0, cr<1, 2>" :: "a"(fcr) : "memory");
        int mode=__fe_getround();
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=(uint32_t)mode;
        if (mode!=expected[c]) return 10+(int)c;
    }
    __asm__ volatile("mtcr %0, cr<1, 2>" :: "a"(saved_fcr) : "memory");
    uint32_t zero=0, fpsr;
    __asm__ volatile("mtcr %0, cr<2, 2>" :: "a"(zero) : "memory");
    __fe_raise_inexact();
    __asm__ volatile("mfcr %0, cr<2, 2>" : "=a"(fpsr));
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=fpsr;
    /* Hardware FESR cause bits occupy the upper byte.  QEMU reports 0x9000
     * for this inexact divide; retain the full word in the observable log. */
    return (fpsr&0x1000u)?0:20;
}
