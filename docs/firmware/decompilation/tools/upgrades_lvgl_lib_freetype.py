"""
Firmware LOW-confidence function upgrades: LVGL, lib, and FreeType modules.

Identified by matching 2-3+ characteristic patterns from known SDK source code.
Analysis date: 2026-03-07
"""

upgrades = {
    # =========================================================================
    # FreeType2 Core (lvgl.lv_freetype module)
    # =========================================================================

    '0x00511876': (
        'FT_Get_Module_Interface_simple', 'lvgl.lv_freetype', 'HIGH',
        '# Calls FT_Get_Module (FUN_0051183c), returns vtable+0x14 (module_interface). '
        'String refs: "psaux", "postscript-cmaps" in callers. 2 patterns: '
        'vtable deref *piVar1+0x14, null-guard on FT_Get_Module return # was: lvgl_lv_freetype_helper_1876'
    ),

    '0x0051188a': (
        'ft_module_get_interface', 'lvgl.lv_freetype', 'HIGH',
        '# Recursive module interface lookup: dispatches through vtable+0x20 (get_interface callback), '
        'iterates child modules if param_3!=0. String refs: "cff_load", "postscript-cmaps" in callers. '
        '3 patterns: vtable dispatch at +0x20, child iteration at +0x14/+0x10, recursive search # was: lvgl_lv_freetype_helper_188a'
    ),

    '0x005128f4': (
        'FT_Open_Face_load_services', 'lvgl.lv_freetype', 'MEDIUM',
        '# Iterates 9 service slots (iVar2<9), calls vtable-dispatched loaders from DAT_00512b98 table. '
        'Uses FT_Stream_Seek. 2 patterns: 9-slot iteration, function pointer table dispatch # was: lvgl_lv_freetype_callee_28f4'
    ),

    '0x0051151a': (
        'ft_glyphslot_set_charmap', 'lvgl.lv_freetype', 'MEDIUM',
        '# Reads face->driver->library (offset chain +4,+0x60,+4), checks cached charmap at +0x9c, '
        'calls ft_glyph_find_by_charcode. 2 patterns: face/driver/library chain, charmap cache check # was: lvgl_lv_freetype_callee_151a'
    ),

    '0x00512476': (
        'ft_property_get', 'lvgl.lv_freetype', 'MEDIUM',
        '# String-based property dispatch (3 branches with strcmp via FUN_00468260). '
        'First branch copies 8 words (BBox?), second copies 1 word, third copies 1 byte. '
        'Returns 0 on match, 0xC on unknown. 2 patterns: triple-strcmp dispatch, structured property copy # was: lvgl_lv_freetype_page_callee_2476'
    ),

    '0x00513f68': (
        'lv_freetype_cache_node_free_outline', 'lvgl.lv_freetype', 'MEDIUM',
        '# Thin wrapper: calls lv_draw_buf_destroy(param_1+8). Frees a draw buffer associated '
        'with a font cache entry. 2 patterns: single deref at +8, delegates to lv_draw_buf_destroy # was: lvgl_lv_freetype_page_callee_3f68'
    ),

    '0x005b7b26': (
        'cff_builder_init', 'lvgl.lv_freetype', 'HIGH',
        '# Initializes 8-field structure: stores 3 params, zeros fields 3/5/6/7, sets field 4=10 (default capacity). '
        'Called from CFF outline builder context. 3 patterns: 8-field struct init, default capacity=10, '
        'CFF caller context (cf2_stack_getArg callers) # was: lvgl_lv_freetype_helper_7b26'
    ),

    '0x005ba3ee': (
        'cf2_interpT2CharString_hints', 'lvgl.lv_freetype', 'MEDIUM',
        '# CFF Type2 charstring hint processing. Calls cf2_stack_count, cf2_stack_getArg, cf2_stack_clear. '
        'Processes hint pairs (odd/even iteration), reads stem widths. '
        '3 patterns: stack count/get/clear sequence, paired hint iteration, recursive self-call # was: lvgl_lv_freetype_helper_a3ee'
    ),

    '0x00538586': (
        'lv_freetype_mem_pool_alloc', 'lvgl.lv_freetype', 'MEDIUM',
        '# Thin wrapper: calls lv_mem_pool_init_3(DAT_005385dc, param_1). '
        'Allocates from LVGL FreeType memory pool global. 2 patterns: single global DAT_005385dc, '
        'delegates to lv_mem_pool_init_3 # was: lvgl_lv_freetype_propagated_005385ac_wrapper'
    ),

    '0x005d0fd2': (
        'cff_decoder_clear_subrs', 'lvgl.lv_freetype', 'MEDIUM',
        '# Clears 2 entries at param_2*8+0x1b8 and param_2*8+0x1bc in decoder state. '
        'Zeroes subroutine pointers. 2 patterns: 8-byte stride at 0x1b8 base, paired zero-write # was: lvgl_lv_freetype_helper_0fd2'
    ),

    '0x005d0f9a': (
        'cff_decoder_set_subrs', 'lvgl.lv_freetype', 'MEDIUM',
        '# Copies from param_2*8+0x1b8 array into decoder state at 0x168/0x170, '
        'stores index at 0x164 and param_3 at 0x16c. Sets up subroutine context. '
        '2 patterns: 8-byte stride read at 0x1b8, structured copy to 0x164-0x170 # was: lvgl_lv_freetype_helper_0f9a'
    ),

    '0x005d10b4': (
        'cff_check_points_realloc', 'lvgl.lv_freetype', 'HIGH',
        '# Conditional realloc: if *param_2 < param_5, calls FT_RENEW_ARRAY (FUN_00513620) '
        'with old_size=param_3*old_count, new_size=param_3*param_5. Updates capacity. '
        '3 patterns: capacity check, FT_RENEW_ARRAY call, size=stride*count math # was: lvgl_lv_freetype_helper_10b4'
    ),

    '0x0057c60a': (
        'cff_charset_cid_to_gindex', 'lvgl.lv_freetype', 'MEDIUM',
        '# Array lookup: if param_2 < *(param_1+0x54c), returns *(*(param_1+0x550)+param_2*4). '
        'CFF charset glyph index lookup. 2 patterns: bounds check at +0x54c, array deref at +0x550 # was: lvgl_lv_freetype_helper_0057c60a'
    ),

    '0x0057d76c': (
        'cff_font_done', 'lvgl.lv_freetype', 'MEDIUM',
        '# Frees 4 allocations via ft_mem_free at offsets 0x284, 0x23c, 0x244, 0x250, '
        'calls FUN_0057c204 (cleanup at +0x260). CFF font destructor. '
        '2 patterns: 4x ft_mem_free+zero pattern, CFF-specific offsets # was: lvgl_lv_freetype_helper_0057d76c'
    ),

    '0x0057519a': (
        'af_face_globals_compute_style_coverage', 'lvgl.lv_freetype', 'MEDIUM',
        '# Auto-hinter style detection: iterates character ranges (DAT_0057526c template), '
        'calls sequence of af_* helpers, checks consistency across samples. '
        'Sets *(param_1+0x20) = is_fixed_width flag. '
        '2 patterns: character range template copy, consistency check loop # was: lvgl_lv_freetype_neighbor_0057519a'
    ),

    # --- FreeType cmap validators (sfnt/ttcmap.c) ---

    '0x005c0052': (
        'sfnt_get_interface', 'lvgl.lv_freetype', 'HIGH',
        '# Thin wrapper: calls ft_service_list_lookup(DAT_005c0a44). '
        'Module get_interface callback for sfnt driver. '
        '2 patterns: single-arg delegation to ft_service_list_lookup, static service list # was: module_callee_0050F3C8'
    ),

    '0x005c1ad0': (
        'tt_cmap4_validate', 'lvgl.lv_freetype', 'HIGH',
        '# TrueType cmap format 4 validator. 256-entry segment loop, big-endian 16-bit reads, '
        'boundary checks against validator limits at +0x84/+0x88, right-shift by 3 for byte offsets, '
        '8-byte record stride. Calls ft_validator_error on failure. '
        '3 patterns: 256-entry loop, BE16 reads, format-4 specific segment structure # was: module_callee_0050F408_1ad0'
    ),

    '0x005c2a54': (
        'tt_cmap8_validate', 'lvgl.lv_freetype', 'HIGH',
        '# TrueType cmap format 8 validator. Header size 0x2010 (12 + 0x2000 bitmap), '
        'validates groups with start<=end ordering, BE32 reads, bitmap bit-checking at byte[offset>>3]. '
        '3 patterns: 0x2010 header size, bitmap validation, 12-byte group records # was: module_callee_0050F408_2a54'
    ),

    '0x005c300a': (
        'tt_cmap12_validate', 'lvgl.lv_freetype', 'HIGH',
        '# TrueType cmap format 12 validator. 0x10 header + 12-byte segmented groups, '
        'BE32 reads for start/end/glyphID, ascending order check, glyph ID range validation. '
        'No bitmap (distinguishes from format 8). '
        '3 patterns: 0x10 header, 12-byte groups, glyph range subtraction check # was: module_callee_0050F408_300a'
    ),

    '0x005c33c8': (
        'tt_cmap13_validate', 'lvgl.lv_freetype', 'HIGH',
        '# TrueType cmap format 13 validator. Same structure as format 12 (0x10 header + 12-byte groups) '
        'but simpler glyph ID validation (uses <= instead of range subtraction). '
        'Many-to-one mapping format. '
        '2 patterns: same structure as cmap12 but simpler startGlyphID check # was: module_callee_0050F408_33c8'
    ),

    # --- TrueType table loading (sfnt) ---

    '0x005c42e4': (
        'tt_face_get_kerning_func', 'lvgl.lv_freetype', 'MEDIUM',
        '# Vtable dispatch: calls *(*(param_1+0xc)+0x30)(), returns 0x96 if null. '
        'Gets kerning function pointer from face driver. '
        '2 patterns: vtable at +0xc then +0x30, error 0x96 on null # was: lvgl_lv_freetype_page_callee_42e4'
    ),

    '0x005c4486': (
        'tt_face_done_kern', 'lvgl.lv_freetype', 'MEDIUM',
        '# Frees kern table data: FT_Stream_Close at (param_1+0x304), zeros 4 fields. '
        'Kern table destructor. 2 patterns: stream close + 4-field zero at 0x304-0x314 # was: lvgl_lv_freetype_page_callee_4486'
    ),

    '0x005c4954': (
        'tt_face_get_location', 'lvgl.lv_freetype', 'MEDIUM',
        '# Reads glyph location from loca table. Handles short (param_2==0) and long format. '
        'Gets memory from face->memory at +0x68, calls FT_Stream_ReadAt. '
        '2 patterns: loca format branch, stream read with offset calculation # was: lvgl_lv_freetype_page_callee_4954'
    ),

    '0x005c4d02': (
        'tt_face_free_name', 'lvgl.lv_freetype', 'HIGH',
        '# Frees two arrays: 0x14-byte stride records at +0x164 (name records), '
        '0xc-byte stride records at +0x16c (lang tags). Zeros counts at +0x15c, +0x168, +0x158, +0x160. '
        'Uses ft_mem_free for each element + array pointer. '
        '3 patterns: dual array free, 0x14/0xc strides, 6-field cleanup # was: lvgl_lv_freetype_page_callee_4d02'
    ),

    '0x005d60dc': (
        'tt_face_load_gasp', 'lvgl.lv_freetype', 'MEDIUM',
        '# Table loader: vtable dispatch at +0x204 with tag constant, FT_Stream_ExtractFrame, '
        'stores length at +0x288 and data at +0x28c. Zeros both on failure. '
        '2 patterns: vtable table access + extract frame, paired length/data storage # was: module_callee_00512E16'
    ),

    # =========================================================================
    # lib module - IEEE 754 / math functions
    # =========================================================================

    '0x0054b970': (
        'frexpf', 'lib', 'HIGH',
        '# IEEE 754 float decomposition wrapper. Calls FUN_0054b984 which extracts '
        'exponent via (param_1<<1)>>0x18, handles denormals with LZCOUNT, special cases 0 and INF/NaN. '
        'Used in powf() implementation with ldexpf. '
        '3 patterns: exponent extraction, denormal renormalization with LZCOUNT, '
        'mantissa/exponent split # was: lib_helper_b970'
    ),

    '0x0053a9d8': (
        'roundf', 'lvgl', 'HIGH',
        '# IEEE 754 single-precision round-to-nearest. Extracts biased exponent via (param_1<<1)>>0x18, '
        'subtracts bias 0x7e, masks mantissa bits with 0xffffff>>shift. '
        'Returns sign-preserved zero for small values, pass-through for large values. '
        '3 patterns: exponent-0x7e bias, mantissa mask 0xffffff>>shift, '
        'banker rounding via +uVar1 & ~uVar1 # was: lvgl_helper_a9d8'
    ),

    # =========================================================================
    # lib module - FreeType functions misclassified as lib
    # =========================================================================

    '0x00511e64': (
        'FT_Outline_Copy', 'lvgl.lv_freetype', 'HIGH',
        '# Copies FT_Outline: points at count*8 (FT_Vector=8 bytes), tags at count*1, '
        'contours at num_contours*2 (short array). Checks n_points and n_contours match. '
        'Returns 0x14 (FT_Err_Invalid_Handle) on NULL, 6 (FT_Err_Invalid_Argument) on mismatch. '
        '3 patterns: 3-part copy (points/tags/contours), stride 8/1/2, '
        'dimension equality check # was: module_callee_00439BE4_1e64'
    ),

    '0x005bdcce': (
        'af_axis_hints_new_segment', 'lvgl.lv_freetype', 'MEDIUM',
        '# Auto-hinter segment builder. Iterates hint pairs, inserts into sorted arrays '
        'at 8-word (32-byte) stride. Uses memmove (FUN_00439c04) for insertion shifts. '
        'Separate arrays for horizontal/vertical axes. '
        '2 patterns: 32-byte record stride, sorted insertion with memmove # was: module_callee_00439C04'
    ),

    '0x005bddb0': (
        'af_glyph_hints_align_edge_points', 'lvgl.lv_freetype', 'MEDIUM',
        '# Auto-hinter edge alignment. Processes 4 quadrants (offsets 0x81, 0x102, 0x183 = '
        '129*{1,2,3} entries). Calls af_axis_hints_new_segment, then adjusts stem widths '
        'with min-distance spacing. 2 patterns: 0x81/0x102/0x183 quadrant offsets, '
        'bidirectional edge adjustment loop # was: module_callee_005BDCCE'
    ),

    '0x005bf074': (
        'ps_unicodes_char_index', 'lvgl.lv_freetype', 'HIGH',
        '# Binary search in sorted Unicode charmap pairs (8-byte stride). '
        'Key masked with 0x7FFFFFFF (high bit = variant selector flag). '
        'Midpoint: (hi-lo)>>4)*2. Returns value at match[1] or 0. '
        '3 patterns: binary search with 8-byte pairs, 0x7FFFFFFF key mask, '
        'paired key/value return # was: lib_page_callee_f074'
    ),

    # =========================================================================
    # LVGL core functions
    # =========================================================================

    '0x0044ede8': (
        'lv_anim_path_linear', 'lvgl', 'HIGH',
        '# LVGL animation linear interpolation: start + ((end - start) * path_value >> 10). '
        'Reads start_value at +0x24, end_value at +0x2c, current at +0x30/+0x34. '
        'The >>10 is LVGL 10-bit fixed-point (1024 = 100%). '
        '3 patterns: start/end at +0x24/+0x2c, >>10 fixed-point scale, '
        'path function call chain # was: module_callee_00481556_ede8'
    ),

    '0x0047cff8': (
        'lv_draw_buf_pool_init', 'lvgl', 'MEDIUM',
        '# Initializes draw buffer pool: allocates memory (FUN_004ca05c with size param), '
        'creates mutex (FUN_00477378), zeros count/max/capacity fields. '
        'Called 3 times with sizes 0x2d000, 0xcd000, 0x400 (3-tier pool). '
        '2 patterns: alloc+mutex creation, 6-field struct init # was: module_callee_0046D18E_cff8'
    ),

    '0x0047d4f6': (
        'lv_draw_dispatch', 'lvgl', 'MEDIUM',
        '# Draw task dispatcher: single-display shortcut (calls lv_draw_buf_create if count==1 at +0x140), '
        'otherwise iterates draw unit linked list via FUN_0047d512 checking state/type. '
        '2 patterns: single-display fast path, draw unit iteration with state check # was: module_callee_0047D8B8'
    ),
}
