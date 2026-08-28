/*
 * SPDX-License-Identifier: FTL
 *
 * Isolated face-loader policy boundary for the authenticated FreeType 2.9.1
 * base-module source candidate.  See third_party/freetype/LICENSE.
 */

#ifndef OPEN_CFW_RUNTIME_FREETYPE_BASE_CLUSTER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREETYPE_BASE_CLUSTER_CANDIDATE_H

#include "runtime_freetype_base_candidate.h"

enum open_cfw_freetype_face_policy {
    /* Match stock: scan drivers, then retain upstream Mac/rfork fallback. */
    OPEN_CFW_FREETYPE_FACE_UPSTREAM_AUTODETECT = 0,
    /* Bypass cross-driver and Mac/rfork fallback for a known TrueType blob. */
    OPEN_CFW_FREETYPE_FACE_TRUETYPE_ONLY = 1,
    /* Bypass cross-driver and Mac/rfork fallback for a known CFF blob. */
    OPEN_CFW_FREETYPE_FACE_CFF_ONLY = 2
};

/*
 * The caller owns data and must keep it immutable until the returned face is
 * released.  Strict policies use FreeType's public FT_OPEN_DRIVER boundary;
 * no loader implementation is copied or replaced by this adapter.
 */
FT_Error open_cfw_freetype_base_open_memory(
    const struct open_cfw_freetype_base_candidate *candidate,
    const unsigned char *data,
    size_t size,
    long face_index,
    enum open_cfw_freetype_face_policy policy,
    FT_Face *face
);

FT_Error open_cfw_freetype_base_reference_face(FT_Face face);
FT_Error open_cfw_freetype_base_release_face(FT_Face face);

/* Public-source bridge that keeps glyph-slot internals behind FreeType. */
FT_Error open_cfw_freetype_base_load_and_render(
    FT_Face face,
    FT_UInt glyph_index,
    FT_Int32 load_flags,
    FT_Render_Mode render_mode
);

#endif
