/*
 * SPDX-License-Identifier: FTL
 *
 * Public-property adapter for the authenticated FreeType 2.9.1 TrueType
 * driver source candidate.  See third_party/freetype/LICENSE.
 */

#include "runtime_freetype_truetype_candidate.h"

#include <ft2build.h>
#include FT_MODULE_H

FT_Error open_cfw_freetype_truetype_set_interpreter(
    FT_Library library,
    FT_UInt version
)
{
    if (library == NULL) {
        return FT_Err_Invalid_Library_Handle;
    }
    return FT_Property_Set(
        library,
        "truetype",
        "interpreter-version",
        &version
    );
}

FT_Error open_cfw_freetype_truetype_get_interpreter(
    FT_Library library,
    FT_UInt *version
)
{
    if (version != NULL) {
        *version = 0U;
    }
    if (library == NULL) {
        return FT_Err_Invalid_Library_Handle;
    }
    if (version == NULL) {
        return FT_Err_Invalid_Argument;
    }
    return FT_Property_Get(
        library,
        "truetype",
        "interpreter-version",
        version
    );
}
