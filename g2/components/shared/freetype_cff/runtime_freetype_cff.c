/*
 * SPDX-License-Identifier: FTL
 *
 * Public policy boundary for the authenticated FreeType 2.9.1 CFF driver.
 * See third_party/freetype/LICENSE for the FreeType Project License.
 */

#include "runtime_freetype_cff.h"

#include <stddef.h>

static const char open_cfw_freetype_cff_module[] = "cff";
static const char open_cfw_freetype_cff_hinting_engine[] = "hinting-engine";
static const char open_cfw_freetype_cff_no_stem_darkening[] =
    "no-stem-darkening";
static const char open_cfw_freetype_cff_darkening_parameters[] =
    "darkening-parameters";

_Static_assert(
    OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT == 8,
    "FreeType CFF darkening property ABI changed"
);
_Static_assert(
    FT_CFF_HINTING_ADOBE == 1,
    "FreeType 2.9.1 Adobe hinting-engine value changed"
);

static FT_Error open_cfw_freetype_cff_check_library(FT_Library library)
{
    if (library == NULL) {
        return FT_Err_Invalid_Library_Handle;
    }
    return FT_Err_Ok;
}

static int open_cfw_freetype_cff_darkening_parameters_are_valid(
    const FT_Int parameters[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT]
)
{
    size_t index;

    if (parameters == NULL) {
        return 0;
    }
    for (index = 0U;
         index < OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT;
         index += 2U) {
        if (parameters[index] < 0 || parameters[index + 1U] < 0 ||
            parameters[index + 1U] > 500) {
            return 0;
        }
    }
    return parameters[0] <= parameters[2] &&
        parameters[2] <= parameters[4] &&
        parameters[4] <= parameters[6];
}

FT_Error open_cfw_freetype_cff_set_hinting_engine(
    FT_Library library,
    FT_UInt engine
)
{
    FT_Error error = open_cfw_freetype_cff_check_library(library);

    if (error != FT_Err_Ok) {
        return error;
    }
    if (engine != FT_CFF_HINTING_ADOBE) {
        return FT_Err_Invalid_Argument;
    }
    return FT_Property_Set(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_hinting_engine,
        &engine
    );
}

FT_Error open_cfw_freetype_cff_get_hinting_engine(
    FT_Library library,
    FT_UInt *engine
)
{
    FT_Error error;

    if (engine == NULL) {
        return FT_Err_Invalid_Argument;
    }
    *engine = 0U;
    error = open_cfw_freetype_cff_check_library(library);
    if (error != FT_Err_Ok) {
        return error;
    }
    return FT_Property_Get(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_hinting_engine,
        engine
    );
}

FT_Error open_cfw_freetype_cff_set_no_stem_darkening(
    FT_Library library,
    FT_Bool disabled
)
{
    FT_Error error = open_cfw_freetype_cff_check_library(library);

    if (error != FT_Err_Ok) {
        return error;
    }
    if (disabled > 1U) {
        return FT_Err_Invalid_Argument;
    }
    return FT_Property_Set(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_no_stem_darkening,
        &disabled
    );
}

FT_Error open_cfw_freetype_cff_get_no_stem_darkening(
    FT_Library library,
    FT_Bool *disabled
)
{
    FT_Error error;

    if (disabled == NULL) {
        return FT_Err_Invalid_Argument;
    }
    *disabled = 0U;
    error = open_cfw_freetype_cff_check_library(library);
    if (error != FT_Err_Ok) {
        return error;
    }
    return FT_Property_Get(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_no_stem_darkening,
        disabled
    );
}

FT_Error open_cfw_freetype_cff_set_darkening_parameters(
    FT_Library library,
    const FT_Int parameters[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT]
)
{
    FT_Error error = open_cfw_freetype_cff_check_library(library);
    FT_Int validated[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT];
    size_t index;

    if (error != FT_Err_Ok) {
        return error;
    }
    if (!open_cfw_freetype_cff_darkening_parameters_are_valid(parameters)) {
        return FT_Err_Invalid_Argument;
    }
    for (index = 0U;
         index < OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT;
         index++) {
        validated[index] = parameters[index];
    }
    return FT_Property_Set(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_darkening_parameters,
        validated
    );
}

FT_Error open_cfw_freetype_cff_get_darkening_parameters(
    FT_Library library,
    FT_Int parameters[OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT]
)
{
    FT_Error error;
    size_t index;

    if (parameters == NULL) {
        return FT_Err_Invalid_Argument;
    }
    for (index = 0U;
         index < OPEN_CFW_FREETYPE_CFF_DARKENING_PARAMETER_COUNT;
         index++) {
        parameters[index] = 0;
    }
    error = open_cfw_freetype_cff_check_library(library);
    if (error != FT_Err_Ok) {
        return error;
    }
    return FT_Property_Get(
        library,
        open_cfw_freetype_cff_module,
        open_cfw_freetype_cff_darkening_parameters,
        parameters
    );
}
