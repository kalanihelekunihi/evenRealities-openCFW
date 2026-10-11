/* Archive soft-float caller names, each at the matching original math body. */
#include "../float_runtime_offline/math.c"
__asm__(".global stock_floorf\n.set stock_floorf, audio_floorf\n"
        ".global stock_roundf\n.set stock_roundf, audio_roundf\n"
        ".global stock_ceilf\n.set stock_ceilf, audio_ceilf\n"
        ".global stock_fmodf\n.set stock_fmodf, audio_fmodf\n");
