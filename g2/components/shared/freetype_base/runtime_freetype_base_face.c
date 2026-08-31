/*
 * SPDX-License-Identifier: FTL
 *
 * Isolated face-loader policy boundary for the authenticated FreeType 2.9.1
 * base-module source admission.  See third_party/freetype/LICENSE.
 */

#include "runtime_freetype_base_face.h"

#include <stdint.h>

static const char *open_cfw_freetype_policy_driver(
    enum open_cfw_freetype_face_policy policy
)
{
    switch (policy) {
    case OPEN_CFW_FREETYPE_FACE_TRUETYPE_ONLY:
        return "truetype";
    case OPEN_CFW_FREETYPE_FACE_CFF_ONLY:
        return "cff";
    default:
        return NULL;
    }
}

FT_Error open_cfw_freetype_base_open_memory(
    const struct open_cfw_freetype_base_state *state,
    const unsigned char *data,
    size_t size,
    long face_index,
    enum open_cfw_freetype_face_policy policy,
    FT_Face *face
)
{
    FT_Library library;
    FT_Open_Args arguments = {0};
    FT_Module driver;
    const char *driver_name;

    if (face != NULL) {
        *face = NULL;
    }
    library = open_cfw_freetype_base_library(state);
    if (library == NULL || data == NULL || size == 0U ||
        size > (size_t)INT32_MAX || face == NULL) {
        return FT_Err_Invalid_Argument;
    }
    if (policy == OPEN_CFW_FREETYPE_FACE_UPSTREAM_AUTODETECT) {
        return FT_New_Memory_Face(
            library,
            (const FT_Byte *)data,
            (FT_Long)size,
            (FT_Long)face_index,
            face
        );
    }

    driver_name = open_cfw_freetype_policy_driver(policy);
    if (driver_name == NULL) {
        return FT_Err_Invalid_Argument;
    }
    driver = FT_Get_Module(library, driver_name);
    if (driver == NULL) {
        return FT_Err_Missing_Module;
    }

    arguments.flags = FT_OPEN_MEMORY | FT_OPEN_DRIVER;
    arguments.memory_base = (const FT_Byte *)data;
    arguments.memory_size = (FT_Long)size;
    arguments.driver = driver;
    return FT_Open_Face(library, &arguments, (FT_Long)face_index, face);
}

FT_Error open_cfw_freetype_base_reference_face(FT_Face face)
{
    if (face == NULL) {
        return FT_Err_Invalid_Face_Handle;
    }
    return FT_Reference_Face(face);
}

FT_Error open_cfw_freetype_base_release_face(FT_Face face)
{
    if (face == NULL) {
        return FT_Err_Invalid_Face_Handle;
    }
    return FT_Done_Face(face);
}

FT_Error open_cfw_freetype_base_load_and_render(
    FT_Face face,
    FT_UInt glyph_index,
    FT_Int32 load_flags,
    FT_Render_Mode render_mode
)
{
    FT_Error error;

    if (face == NULL || face->glyph == NULL) {
        return FT_Err_Invalid_Face_Handle;
    }
    error = FT_Load_Glyph(face, glyph_index, load_flags);
    if (error != FT_Err_Ok) {
        return error;
    }
    return FT_Render_Glyph(face->glyph, render_mode);
}

