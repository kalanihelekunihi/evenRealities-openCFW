#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern void *gx8002_resident_memcpy_25738(void *, const void *, uint32_t);

int main(void) {
    static const unsigned lengths[] = {0, 1, 3, 4, 15, 16, 17, 64, 127};
    unsigned cases = 0;
    for (unsigned da = 0; da < 4; ++da) {
        for (unsigned sa = 0; sa < 4; ++sa) {
            for (unsigned i = 0; i < sizeof(lengths)/sizeof(lengths[0]); ++i) {
                uint8_t d[160], s[160];
                for (unsigned k = 0; k < sizeof(d); ++k) { d[k] = 0xa5; s[k] = (uint8_t)(k*17u+3u); }
                void *ret = gx8002_resident_memcpy_25738(d+da, s+sa, lengths[i]);
                if (ret != d+da) return 1;
                for (unsigned k = 0; k < lengths[i]; ++k) if (d[da+k] != s[sa+k]) return 2;
                for (unsigned k = 0; k < da; ++k) if (d[k] != 0xa5) return 3;
                for (unsigned k = da+lengths[i]; k < sizeof(d); ++k) if (d[k] != 0xa5) return 4;
                ++cases;
            }
        }
    }
    printf("%u memcpy alias vectors PASS\n", cases);
    return 0;
}
