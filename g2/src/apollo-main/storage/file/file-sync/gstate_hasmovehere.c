/* LittleFS global-move match, stock 0x4caf5c. */
#include <stdint.h>
int32_t g2_lfs_gstate_hasmovehere(void *state,const void *pair) {
    const uint32_t *g=(const uint32_t *)state,*p=(const uint32_t *)pair;
    if((g[0]&0x70000000u)==0u) return 0;
    return g[1]==p[0] || g[2]==p[1] || g[1]==p[1] || g[2]==p[0];
}
