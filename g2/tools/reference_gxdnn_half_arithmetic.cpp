// SPDX-License-Identifier: MIT
// Source-built host reference. Not a target firmware implementation.
#define HALF_ROUND_TIES_TO_EVEN 1
#include "half.hpp"
#include <cstdint>
#include <cstdio>
// Binary input: operation, operand A, operand B (three uint16_t words).
// Output: one uint16_t result. Operations match choose_calc_func 0..3.
int main()
{
    uint16_t words[3];
    for (;;) {
        const size_t n=std::fread(words,sizeof(uint16_t),3,stdin);
        if (!n) return std::ferror(stdin)?1:0;
        if (n!=3 || words[0]>3) return 2;
        const float a=half_float::detail::half2float<float>(words[1]);
        const float b=half_float::detail::half2float<float>(words[2]);
        float result;
        switch(words[0]) {
        case 0: result=a+b;break;
        case 1: result=a-b;break;
        case 2: result=a*b;break;
        default: result=a/b;break;
        }
        uint16_t bits=half_float::detail::float2half<std::round_to_nearest>(result);
        if (std::fwrite(&bits,sizeof(bits),1,stdout)!=1) return 3;
    }
}
