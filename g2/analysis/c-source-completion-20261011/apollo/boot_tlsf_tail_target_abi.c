/* Target-ABI proof for the six stock 0x4341a8 TLSF constant words.
 * Include the exact selected pinned provider source, then check its actual
 * types and enum under the selected Cortex-M55 compilation flags. */
#include "../../../components/bootloader/allocator/upstream/tlsf.c"

_Static_assert(sizeof(size_t) == 4u, "target size_t");
_Static_assert((1u << 0) == 1u && (1u << 1) == 2u, "status bits");
_Static_assert(offsetof(block_header_t, size) + sizeof(size_t) == 8u,
               "block start offset");
_Static_assert(sizeof(block_header_t) - sizeof(block_header_t *) == 12u,
               "minimum block size");
_Static_assert(FL_INDEX_MAX == 30, "target max shift");
_Static_assert((1u << FL_INDEX_MAX) == 0x40000000u,
               "maximum block size");
