#include <stdint.h>

/* Function identities from authenticated stock tables 0x334b1c, 0x334e80,
 * 0x335398 and 0x335730.  Each nonzero cell is a source-symbol relocation,
 * never an absolute stock code address.  Final table VMA/caller ABI remains
 * a linker/integration contract. */
#define CALLBACK1(hex) \
    extern uint32_t opencfw_em9305_init_transition_##hex(uintptr_t)
CALLBACK1(3168b0); CALLBACK1(316698); CALLBACK1(3166d8);
CALLBACK1(316894); CALLBACK1(3166bc); CALLBACK1(3166a0);
CALLBACK1(3166c4); CALLBACK1(31a554); CALLBACK1(31a538);
CALLBACK1(31a408); CALLBACK1(31a434); CALLBACK1(31a58c);
CALLBACK1(324964); CALLBACK1(3249ac); CALLBACK1(3249bc);
CALLBACK1(3249b8); CALLBACK1(32d0f4); CALLBACK1(32d10c);
CALLBACK1(32d2dc);
extern uint32_t opencfw_em9305_init_transition_32d108(uint32_t);
extern uint32_t opencfw_em9305_init_transition_dispatch_316704(void);
extern uint32_t opencfw_em9305_init_transition_secondary_32d138(void);

#define S(hex) ((uintptr_t)&opencfw_em9305_init_transition_##hex)
#define D ((uintptr_t)&opencfw_em9305_init_transition_dispatch_316704)
#define N ((uintptr_t)&opencfw_em9305_init_transition_secondary_32d138)

const uintptr_t opencfw_em9305_init_transition_callbacks_334b1c[20]={
    0u,S(3168b0),S(316698),S(3166d8),0u,
    S(316894),S(316698),S(316894),0u,D,
    0u,S(3166bc),S(3166bc),0u,S(3166a0),
    0u,S(3166bc),S(3166bc),0u,S(3166c4)
};
const uint8_t opencfw_em9305_init_transition_states_334b6c[20]={
    0u,1u,0u,1u,0u,3u,1u,2u,1u,0u,
    3u,2u,2u,2u,0u,3u,3u,3u,3u,0u
};

const uintptr_t opencfw_em9305_init_transition_callbacks_334e80[16]={
    0u,S(31a554),0u,0u,0u,S(31a538),S(31a408),S(31a434),
    0u,S(31a538),0u,S(31a58c),0u,S(31a538),0u,S(31a58c)
};
const uint8_t opencfw_em9305_init_transition_states_334ec0[16]={
    0u,1u,0u,0u,3u,1u,0u,0u,
    3u,2u,2u,0u,3u,3u,3u,0u
};

const uintptr_t opencfw_em9305_init_transition_callbacks_335398[20]={
    0u,S(324964),0u,0u,0u,S(3249ac),0u,S(3249ac),
    0u,S(3249bc),0u,0u,0u,S(3249b8),0u,0u,
    0u,0u,S(3249b8),0u
};
const uint8_t opencfw_em9305_init_transition_states_3353e8[20]={
    0u,1u,0u,0u,0u,3u,1u,2u,1u,2u,
    3u,2u,2u,0u,2u,3u,3u,3u,0u,3u
};

const uintptr_t opencfw_em9305_init_transition_callbacks_335730[24]={
    0u,N,0u,0u,0u,0u,S(32d0f4),0u,
    0u,S(32d10c),S(32d108),0u,0u,0u,0u,0u,
    0u,S(32d2dc),0u,0u,0u,0u,0u,S(32d2dc)
};
/* 0x335790 state bytes are already selected in controller_init.c. */

_Static_assert(sizeof(opencfw_em9305_init_transition_callbacks_334b1c)==80u,
    "334b1c pointer table size");
_Static_assert(sizeof(opencfw_em9305_init_transition_callbacks_334e80)==64u,
    "334e80 pointer table size");
_Static_assert(sizeof(opencfw_em9305_init_transition_callbacks_335398)==80u,
    "335398 pointer table size");
_Static_assert(sizeof(opencfw_em9305_init_transition_callbacks_335730)==96u,
    "335730 pointer table size");
#undef S
#undef D
#undef N
#undef CALLBACK1
