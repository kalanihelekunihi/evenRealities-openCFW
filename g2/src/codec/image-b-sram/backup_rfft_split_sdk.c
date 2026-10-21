/* Loaded image B 0x1000efd4 / 0x1000f068.
 * The pinned NationalChip/T-HEAD libdsp source has the same split RFFT and
 * RIFFT arithmetic, pointer walk, five-argument ABI, and zero/Nyquist tails
 * as the authenticated native instruction graph. Compile its actual source
 * under image-B names; do not substitute an opaque library object.
 * Upstream file carries Apache-2.0 license and copyright notice.
 */
#define csky_split_rfft_q15 gx8002_image_b_split_rfft_q15_1000efd4
#define csky_split_rifft_q15 gx8002_image_b_split_rifft_sdk_reference_unselected
#include "../../../../third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source/TransformFunctions/csky_split_rfft_q15.c"
