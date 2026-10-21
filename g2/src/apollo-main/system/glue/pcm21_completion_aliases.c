/* Original PCM2.1 timer, completion, and TON entries under caller names. */
#include "../../audio/pcm21/pcm21-completion/completion.c"

__asm__(".global stock_timer_publish\n.set stock_timer_publish, pcm21_timer_publish\n"
        ".global stock_timer_clear\n.set stock_timer_clear, pcm21_boost_remove\n"
        ".global stock_completion\n.set stock_completion, pcm21_buck_complete\n"
        ".global stock_ton\n.set stock_ton, pcm21_ton\n");
