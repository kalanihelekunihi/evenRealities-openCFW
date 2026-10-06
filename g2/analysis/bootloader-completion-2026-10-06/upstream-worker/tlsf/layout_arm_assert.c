/* Include the pinned implementation to validate its target-side private ABI. */
#include "tlsf.c"

typedef char control_size_matches_bootloader_literal[
        (sizeof(control_t) == 0xc74) ? 1 : -1];
typedef char fl_index_count_matches_image_loops[
        (FL_INDEX_COUNT == 24) ? 1 : -1];
typedef char sl_index_count_matches_image_loops[
        (SL_INDEX_COUNT == 32) ? 1 : -1];
