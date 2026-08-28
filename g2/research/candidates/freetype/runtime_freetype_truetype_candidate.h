/*
 * SPDX-License-Identifier: FTL
 *
 * Public-property adapter for the authenticated FreeType 2.9.1 TrueType
 * driver source candidate.  See third_party/freetype/LICENSE.
 */

#ifndef OPEN_CFW_RUNTIME_FREETYPE_TRUETYPE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREETYPE_TRUETYPE_CANDIDATE_H

#include "runtime_freetype_base_candidate.h"

enum open_cfw_freetype_truetype_interpreter {
    OPEN_CFW_FREETYPE_TRUETYPE_INTERPRETER_V35 = 35,
    OPEN_CFW_FREETYPE_TRUETYPE_INTERPRETER_V40 = 40
};

FT_Error open_cfw_freetype_truetype_set_interpreter(
    FT_Library library,
    FT_UInt version
);

FT_Error open_cfw_freetype_truetype_get_interpreter(
    FT_Library library,
    FT_UInt *version
);

#endif
