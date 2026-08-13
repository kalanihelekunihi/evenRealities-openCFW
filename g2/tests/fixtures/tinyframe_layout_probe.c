#include "TinyFrame.h"

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t prefix_magic;
    TinyFrame upstream_core;
    uint32_t suffix_magic;
} open_cfw_tinyframe_g2_layout_probe_t;

_Static_assert(sizeof(TinyFrame) == 0x7158, "pristine configured core size");
_Static_assert(offsetof(TinyFrame, peer_bit) == 0x08, "upstream peer offset");
_Static_assert(offsetof(TinyFrame, next_id) == 0x0A, "upstream next-id offset");
_Static_assert(offsetof(TinyFrame, state) == 0x0C, "upstream state offset");
_Static_assert(offsetof(TinyFrame, data) == 0x14, "upstream RX buffer offset");
_Static_assert(offsetof(TinyFrame, sendbuf) == 0x601D, "upstream TX buffer offset");
_Static_assert(offsetof(TinyFrame, id_listeners) == 0x642C, "upstream ID listeners");
_Static_assert(offsetof(TinyFrame, type_listeners) == 0x702C, "upstream type listeners");
_Static_assert(offsetof(TinyFrame, generic_listeners) == 0x712C, "upstream generic listeners");
_Static_assert(offsetof(TinyFrame, count_id_lst) == 0x7154, "upstream counters");

_Static_assert(sizeof(open_cfw_tinyframe_g2_layout_probe_t) == 0x7160, "G2 vendor object size");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.peer_bit) == 0x0C, "G2 peer offset");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.data) == 0x18, "G2 RX offset");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.sendbuf) == 0x6021, "G2 TX offset");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.id_listeners) == 0x6430, "G2 ID listeners");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.type_listeners) == 0x7030, "G2 type listeners");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.generic_listeners) == 0x7130, "G2 generic listeners");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, upstream_core.count_id_lst) == 0x7158, "G2 counters");
_Static_assert(offsetof(open_cfw_tinyframe_g2_layout_probe_t, suffix_magic) == 0x715C, "G2 suffix magic");
