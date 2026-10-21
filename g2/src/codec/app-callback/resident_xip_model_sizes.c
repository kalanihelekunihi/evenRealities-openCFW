/* SPDX-License-Identifier: MIT
 * Exact source-owned model size accessors, native XIP 0x10208bf4..0x10208c13.
 * These are five return-immediate functions in the authenticated image.
 */
#include <stdint.h>

int32_t gx8002_xip_model_cmd_size_10208bf4(void) { return 0x23cc; }
int32_t gx8002_xip_model_weight_size_10208bfc(void) { return 0x1d7e0; }
int32_t gx8002_xip_model_ops_size_10208c04(void) { return 0; }
int32_t gx8002_xip_model_data_size_10208c08(void) { return 0x3300; }
int32_t gx8002_xip_model_tmp_size_10208c10(void) { return 4; }
