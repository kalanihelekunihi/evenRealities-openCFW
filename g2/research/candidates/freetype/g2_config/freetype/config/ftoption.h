/*
 * SPDX-License-Identifier: FTL
 *
 * G2 delta over the authenticated FreeType 2.9.1 ftoption.h.  The upstream
 * file remains unmodified.  Every assertion below is recovered independently
 * from the official G2 image; see docs/research/freetype-recovery-audit.md.
 */

#ifndef OPEN_CFW_FREETYPE_G2_FTOPTION_H
#define OPEN_CFW_FREETYPE_G2_FTOPTION_H

#include_next <freetype/config/ftoption.h>

/* Stock FT_Init_FreeType contains no environment-property parser call. */
#undef FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES

/*
 * The authenticated 297-file selection has no gzip implementation.  Keep
 * compressed WOFF tables explicitly unsupported instead of admitting an
 * unauthenticated FT_Gzip_Uncompress provider.
 */
#undef FT_CONFIG_OPTION_USE_ZLIB

#if !defined(TT_CONFIG_OPTION_BYTECODE_INTERPRETER)
#error "G2 FreeType requires the TrueType bytecode interpreter"
#endif
#if TT_CONFIG_OPTION_SUBPIXEL_HINTING != 2
#error "G2 FreeType requires minimal v40 TrueType subpixel hinting"
#endif
#if !defined(TT_CONFIG_OPTION_GX_VAR_SUPPORT)
#error "G2 FreeType requires GX variation support"
#endif
#if !defined(TT_CONFIG_OPTION_EMBEDDED_BITMAPS)
#error "G2 FreeType requires embedded bitmap support"
#endif
#if !defined(FT_CONFIG_OPTION_INCREMENTAL)
#error "G2 FreeType requires incremental loading"
#endif
#if defined(FT_CONFIG_OPTION_PIC)
#error "G2 FreeType uses static non-PIC module classes"
#endif
#if defined(FT_CONFIG_OPTION_SUBPIXEL_RENDERING)
#error "G2 FreeType uses the three-pass LCD fallback"
#endif
#if defined(CFF_CONFIG_OPTION_OLD_ENGINE)
#error "G2 FreeType uses only the Adobe CFF engine"
#endif
#if !defined(AF_CONFIG_OPTION_CJK) || !defined(AF_CONFIG_OPTION_INDIC) || \
    !defined(AF_CONFIG_OPTION_USE_WARPER)
#error "G2 FreeType requires recovered CJK, Indic, and warper autofit guards"
#endif

#endif
