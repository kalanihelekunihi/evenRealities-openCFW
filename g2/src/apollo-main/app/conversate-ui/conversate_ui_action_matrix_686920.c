/* Exact stock route matrix at 0x686920; native handler bodies remain unresolved. */
#include <stdint.h>

typedef uint32_t (*audio_conversate_ui_action_handler)(uint32_t, uint32_t);
typedef struct {
    uint8_t next_state;
    uint8_t reserved[3];
    audio_conversate_ui_action_handler handler;
} audio_conversate_ui_route;

extern uint32_t audio_conversate_ui_route_5b1998(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b1a14(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b29bc(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b2a64(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b2b74(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b2c68(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b2d64(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b30c8(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b32b4(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b3398(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b34a0(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b34b4(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b58e8(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b59fa(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b5b96(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b5bf0(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b5ed2(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b5ef6(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b5f44(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b6426(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b6688(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b68d6(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b6f8e(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b7138(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b74ba(uint32_t, uint32_t);
extern uint32_t audio_conversate_ui_route_5b7556(uint32_t, uint32_t);

__attribute__((used, section(".g2_conversate_ui_action_matrix_686920")))
const audio_conversate_ui_route audio_conversate_ui_action_matrix_686920[7][21] = {
    { /* state 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {3u, {0u, 0u, 0u}, audio_conversate_ui_route_5b58e8}, /* event 1 */
        {3u, {0u, 0u, 0u}, audio_conversate_ui_route_5b59fa}, /* event 2 */
        {1u, {0u, 0u, 0u}, audio_conversate_ui_route_5b30c8}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {0u, {0u, 0u, 0u}, 0}, /* event 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {0u, {0u, 0u, 0u}, 0}, /* event 10 */
        {0u, {0u, 0u, 0u}, 0}, /* event 11 */
        {0u, {0u, 0u, 0u}, 0}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {0u, {0u, 0u, 0u}, 0}, /* event 14 */
        {0u, {0u, 0u, 0u}, 0}, /* event 15 */
        {0u, {0u, 0u, 0u}, 0}, /* event 16 */
        {0u, {0u, 0u, 0u}, 0}, /* event 17 */
        {0u, {0u, 0u, 0u}, 0}, /* event 18 */
        {0u, {0u, 0u, 0u}, 0}, /* event 19 */
        {0u, {0u, 0u, 0u}, 0}, /* event 20 */
    },
    { /* state 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 2 */
        {1u, {0u, 0u, 0u}, audio_conversate_ui_route_5b30c8}, /* event 3 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b2d64}, /* event 4 */
        {0u, {0u, 0u, 0u}, 0}, /* event 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {0u, {0u, 0u, 0u}, 0}, /* event 10 */
        {0u, {0u, 0u, 0u}, 0}, /* event 11 */
        {0u, {0u, 0u, 0u}, 0}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {0u, {0u, 0u, 0u}, 0}, /* event 14 */
        {0u, {0u, 0u, 0u}, 0}, /* event 15 */
        {0u, {0u, 0u, 0u}, 0}, /* event 16 */
        {0u, {0u, 0u, 0u}, 0}, /* event 17 */
        {0u, {0u, 0u, 0u}, 0}, /* event 18 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1998}, /* event 19 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1a14}, /* event 20 */
    },
    { /* state 2 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 2 */
        {0u, {0u, 0u, 0u}, 0}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6426}, /* event 5 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b7138}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b5f44}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {0u, {0u, 0u, 0u}, 0}, /* event 10 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b32b4}, /* event 11 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b2b74}, /* event 12 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b2c68}, /* event 13 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b29bc}, /* event 14 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b2a64}, /* event 15 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b3398}, /* event 16 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34a0}, /* event 17 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34b4}, /* event 18 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1998}, /* event 19 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1a14}, /* event 20 */
    },
    { /* state 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {3u, {0u, 0u, 0u}, audio_conversate_ui_route_5b59fa}, /* event 2 */
        {1u, {0u, 0u, 0u}, audio_conversate_ui_route_5b30c8}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {0u, {0u, 0u, 0u}, 0}, /* event 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {0u, {0u, 0u, 0u}, 0}, /* event 10 */
        {0u, {0u, 0u, 0u}, 0}, /* event 11 */
        {1u, {0u, 0u, 0u}, audio_conversate_ui_route_5b30c8}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {3u, {0u, 0u, 0u}, audio_conversate_ui_route_5b5b96}, /* event 14 */
        {3u, {0u, 0u, 0u}, audio_conversate_ui_route_5b5bf0}, /* event 15 */
        {0u, {0u, 0u, 0u}, 0}, /* event 16 */
        {0u, {0u, 0u, 0u}, 0}, /* event 17 */
        {0u, {0u, 0u, 0u}, 0}, /* event 18 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1998}, /* event 19 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1a14}, /* event 20 */
    },
    { /* state 4 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 2 */
        {0u, {0u, 0u, 0u}, 0}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6426}, /* event 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b68d6}, /* event 9 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6688}, /* event 10 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b32b4}, /* event 11 */
        {0u, {0u, 0u, 0u}, 0}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b5ed2}, /* event 14 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b5ef6}, /* event 15 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b3398}, /* event 16 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34a0}, /* event 17 */
        {4u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34b4}, /* event 18 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1998}, /* event 19 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1a14}, /* event 20 */
    },
    { /* state 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 2 */
        {0u, {0u, 0u, 0u}, 0}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6426}, /* event 5 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b7138}, /* event 6 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b74ba}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b7556}, /* event 10 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b32b4}, /* event 11 */
        {0u, {0u, 0u, 0u}, 0}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6f8e}, /* event 14 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b6f8e}, /* event 15 */
        {2u, {0u, 0u, 0u}, audio_conversate_ui_route_5b3398}, /* event 16 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34a0}, /* event 17 */
        {5u, {0u, 0u, 0u}, audio_conversate_ui_route_5b34b4}, /* event 18 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1998}, /* event 19 */
        {6u, {0u, 0u, 0u}, audio_conversate_ui_route_5b1a14}, /* event 20 */
    },
    { /* state 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 0 */
        {0u, {0u, 0u, 0u}, 0}, /* event 1 */
        {0u, {0u, 0u, 0u}, 0}, /* event 2 */
        {0u, {0u, 0u, 0u}, 0}, /* event 3 */
        {0u, {0u, 0u, 0u}, 0}, /* event 4 */
        {0u, {0u, 0u, 0u}, 0}, /* event 5 */
        {0u, {0u, 0u, 0u}, 0}, /* event 6 */
        {0u, {0u, 0u, 0u}, 0}, /* event 7 */
        {0u, {0u, 0u, 0u}, 0}, /* event 8 */
        {0u, {0u, 0u, 0u}, 0}, /* event 9 */
        {0u, {0u, 0u, 0u}, 0}, /* event 10 */
        {0u, {0u, 0u, 0u}, 0}, /* event 11 */
        {0u, {0u, 0u, 0u}, 0}, /* event 12 */
        {0u, {0u, 0u, 0u}, 0}, /* event 13 */
        {0u, {0u, 0u, 0u}, 0}, /* event 14 */
        {0u, {0u, 0u, 0u}, 0}, /* event 15 */
        {0u, {0u, 0u, 0u}, 0}, /* event 16 */
        {0u, {0u, 0u, 0u}, 0}, /* event 17 */
        {0u, {0u, 0u, 0u}, 0}, /* event 18 */
        {0u, {0u, 0u, 0u}, 0}, /* event 19 */
        {0u, {0u, 0u, 0u}, 0}, /* event 20 */
    },
};

_Static_assert(sizeof(audio_conversate_ui_action_matrix_686920) == 1176u,
               "seven native 21-event route rows");
