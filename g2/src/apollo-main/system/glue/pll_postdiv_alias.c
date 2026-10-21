/* Clock-driver diagnostic name for the same Apollo SYSPLL postdivider entry. */
#include "../../hal/clock/syspll-generator/generator.c"
__asm__(".global stock_pll_generate\n"
        ".set stock_pll_generate, audio_pll_postdiv\n");
