#include <stdint.h>
#include <stdio.h>
#include "clock_popcount_421584.h"
int main(void){
    uint32_t x=0x9e3779b9u;
    for(uint32_t i=0;i<65536u;i++) if(opencfw_boot_clock_popcount(i)!=(uint32_t)__builtin_popcount(i)) return 1;
    for(uint32_t i=0;i<100000u;i++){x=x*1664525u+1013904223u;if(opencfw_boot_clock_popcount(x)!=(uint32_t)__builtin_popcount(x)) return 2;}
    puts("PASS 165536 popcount cases");return 0;
}
