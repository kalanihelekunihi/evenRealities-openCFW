/*
 * SPDX-License-Identifier: FTL
 *
 * Public policy boundary for the authenticated FreeType 2.9.1 CFF driver.
 * See third_party/freetype/LICENSE for the FreeType Project License.
 */

#ifndef OPEN_CFW_RUNTIME_FREETYPE_CFF_H
#define OPEN_CFW_RUNTIME_FREETYPE_CFF_H

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_DRIVER_H
#include FT_MODULE_H

enum {
    OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT = 8
};

/*
 * The recovered G2 build excludes CFF_CONFIG_OPTION_OLD_ENGINE.  Adobe is
 * consequently the only admitted CFF hinting engine.
 */
FT_Error open_cfw_freetype_cff_set_hinting_engine(
    FT_Library library,
    FT_UInt engine
);

FT_Error open_cfw_freetype_cff_get_hinting_engine(
    FT_Library library,
    FT_UInt *engine
);

/* Accept only the public Boolean values 0 and 1. */
FT_Error open_cfw_freetype_cff_set_no_stem_darkening(
    FT_Library library,
    FT_Bool disabled
);

FT_Error open_cfw_freetype_cff_get_no_stem_darkening(
    FT_Library library,
    FT_Bool *disabled
);

/*
 * parameters is {x1, y1, x2, y2, x3, y3, x4, y4}.  X coordinates must be
 * non-negative and monotonic; Y coordinates must lie in [0, 500].
 */
FT_Error open_cfw_freetype_cff_set_darkening_parameters(
    FT_Library library,
    const FT_Int parameters[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT]
);

FT_Error open_cfw_freetype_cff_get_darkening_parameters(
    FT_Library library,
    FT_Int parameters[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT]
);

#endif
