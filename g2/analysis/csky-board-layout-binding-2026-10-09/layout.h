/* Analysis-only little-endian 32-bit layout; not authentic SDK source. */
#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t flags, evad[3], thresholds[3]; } input_view;
typedef struct {
 uint32_t input_source; input_view input[3]; uint32_t output_mask,sadc,pdm;
 uint32_t i2s_in[6],pcm0[6],pcm1[6],logfbank[5],i2s_out[7],spectrum[5];
} board_view;
_Static_assert(sizeof(board_view)==240,"board extent");
_Static_assert(offsetof(board_view,output_mask)==88,"mask");
_Static_assert(offsetof(board_view,pcm1)==148,"pcm1");
_Static_assert(offsetof(board_view,i2s_out)==192,"i2s");
static inline unsigned gain_enum(uint32_t flags) { return (flags>>6)&15; }
static inline unsigned stereo(uint32_t flags) { return (flags>>11)&1; }
