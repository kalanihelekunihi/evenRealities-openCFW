/* SPDX-License-Identifier: MIT */
/* Recovered stock KwsStragegyRun; provenance in gx8002-kws-strategy-frontier.json. */
#include <stddef.h>
struct keyword { char words[40]; short labels[16]; int length, threshold, value, major; };
struct keywords { unsigned count; struct keyword *items; };
struct activation { int index, value; float score; int score_index; void *reverse; };
struct activations { int total; struct activation items[8]; };
_Static_assert(sizeof(struct keyword)==88,"keyword ABI");
_Static_assert(sizeof(struct activation)==20,"activation ABI");
extern struct activations open_cfw_gx8002_activations;
extern struct keywords open_cfw_gx8002_max_keyword_list;
extern int printf(const char *, ...);
const char open_cfw_gx8002_strategy_row[] __attribute__((aligned(1)))="[ST] Kws:%s[%d],th:%d,S:%d,D:%d\n";
const char open_cfw_gx8002_strategy_selected[] __attribute__((aligned(1)))="[ST] Activation ctx:%d,Kws:%s[%d],th:%d,S:%d\n";
static struct keyword *parameter(int index)
{
    /* Stock helper at 0x100264dc is a side-effect-free constant return. */
    return &open_cfw_gx8002_max_keyword_list.items[index];
}
struct activation *open_cfw_gx8002_kws_strategy(void *context)
{
    if (open_cfw_gx8002_activations.total==0) return NULL;
    struct activation *selected=&open_cfw_gx8002_activations.items[0];
    float best=0.f;
    for (int i=0;i<open_cfw_gx8002_activations.total;i++) {
        struct activation *current=&open_cfw_gx8002_activations.items[i];
        int index=current->index;
        float score=current->score;
        struct keyword *p=parameter(index);
        float threshold=(float)p->threshold/10.f;
        float difference;
        if (score<threshold) {
            difference=(score-(threshold-10.f))*0.5f;
            /* Stock fcmpzhss/bt also replaces an unordered result. */
            if (!(difference>=0.f)) difference=0.1f;
        } else difference=score-threshold;
        if (difference>best) { best=difference; selected=current; }
        printf(open_cfw_gx8002_strategy_row,p->words,p->value,
               (int)(10.f*threshold),(int)(10.f*score),(int)(10.f*difference));
    }
    struct keyword *p=parameter(selected->index);
    float threshold=(float)p->threshold/10.f;
    printf(open_cfw_gx8002_strategy_selected,((unsigned *)context)[2],p->words,p->value,
           (int)(10.f*threshold),(int)(10.f*selected->score));
    return selected;
}
