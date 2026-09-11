/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 LVGL v9.3 area-geometry family at
 * 0x00450B80..0x004516F8 (open_cfw_lv_area_get_width through
 * open_cfw_lv_area_align, plus the rounded-corner point helper).  Every
 * function here is a clean-room reconstruction from the Ghidra decompilation
 * of the retained bytes (g2/research/corpus/apollo-main/ghidra/decomp,
 * FUN_00450b80 through FUN_00451082) matched against the public LVGL v9.3
 * `lv_area_t`/`lv_align_t` API contract declared in
 * third_party/lvgl/src/misc/lv_area.h and lv_area_private.h.  See
 * g2/docs/research/g2-lvgl-area-geometry-source-admission.md for the
 * function-by-function derivation and host-oracle verification.
 *
 * `lv_area_t` is reproduced here as a plain four-`int` span
 * {x1, y1, x2, y2} rather than by including the vendored LVGL header, so
 * each leaf below stays a self-contained translation unit with the same
 * memory layout LVGL callers already use.
 */

__attribute__((used, noinline))
int open_cfw_lv_area_get_width(const int *area)
{
    return (area[2] - area[0]) + 1;
}

__attribute__((used, noinline))
int open_cfw_lv_area_get_height(const int *area)
{
    return (area[3] - area[1]) + 1;
}

__attribute__((used, noinline))
unsigned int open_cfw_lv_area_get_size(const int *area)
{
    return (unsigned int)(((area[3] - area[1]) + 1) * ((area[2] - area[0]) + 1));
}

__attribute__((used, noinline))
void open_cfw_lv_area_increase(int *area, int w_extra, int h_extra)
{
    area[0] = area[0] - w_extra;
    area[2] = area[2] + w_extra;
    area[1] = area[1] - h_extra;
    area[3] = area[3] + h_extra;
}

__attribute__((used, noinline))
void open_cfw_lv_area_move(int *area, int x_ofs, int y_ofs)
{
    area[0] = area[0] + x_ofs;
    area[2] = area[2] + x_ofs;
    area[1] = area[1] + y_ofs;
    area[3] = area[3] + y_ofs;
}

__attribute__((used, noinline))
void open_cfw_lv_area_join(int *res, const int *a1, const int *a2)
{
    res[0] = (a1[0] < a2[0]) ? a1[0] : a2[0];
    res[1] = (a1[1] < a2[1]) ? a1[1] : a2[1];
    res[2] = (a2[2] < a1[2]) ? a1[2] : a2[2];
    res[3] = (a2[3] < a1[3]) ? a1[3] : a2[3];
}

__attribute__((used, noinline))
int open_cfw_lv_area_intersect(int *res, const int *a1, const int *a2)
{
    res[0] = (a1[0] > a2[0]) ? a1[0] : a2[0];
    res[1] = (a1[1] > a2[1]) ? a1[1] : a2[1];
    res[2] = (a1[2] < a2[2]) ? a1[2] : a2[2];
    res[3] = (a1[3] < a2[3]) ? a1[3] : a2[3];
    if (res[2] < res[0] || res[3] < res[1]) {
        return 0;
    }
    return 1;
}

/*
 * Distance-squared corner test used by open_cfw_lv_area_is_point_on once it
 * has narrowed the candidate region to one rounded corner's bounding square
 * (FUN_0045163c).  `corner` is a 2r x 2r box anchored so a circle of radius
 * r inscribed in it is exactly the corner's round-rect arc.
 */
__attribute__((used, noinline))
int open_cfw_lv_area_point_within_corner_radius(const int *corner, const int *point)
{
    int radius = (corner[2] - corner[0]) / 2;
    int dx = point[0] - (radius + corner[0]);
    int dy = point[1] - (radius + corner[1]);
    unsigned int distance_sq = (unsigned int)(dx * dx + dy * dy);
    unsigned int radius_sq = (unsigned int)(radius * radius);
    return distance_sq <= radius_sq;
}

/*
 * FUN_00450dd4.  Tests whether `point` lies on `area`, accounting for a
 * rounded-corner radius: first a plain bounding-box test, then (if the box
 * contains the point and radius > 0) a sequence of shrunk corner-square
 * checks that identify which corner (if any) the point falls near, followed
 * by the circular distance test for that corner.  A point in the box but not
 * near any corner is "on" unconditionally.
 */
__attribute__((used, noinline))
int open_cfw_lv_area_is_point_on(const int *area, const int *point, int radius)
{
    int within_bounds =
        (area[0] <= point[0]) && (point[0] <= area[2]) &&
        (area[1] <= point[1]) && (point[1] <= area[3]);
    int width;
    int height;
    int half_min;
    int r;
    int box[4];

    if (!within_bounds) {
        return 0;
    }
    if (radius < 1) {
        return 1;
    }

    width = open_cfw_lv_area_get_width(area);
    height = open_cfw_lv_area_get_height(area);
    half_min = (width / 2 < height / 2) ? width / 2 : height / 2;
    r = (half_min < radius) ? half_min : radius;

    /* Top-left corner square. */
    box[0] = area[0];
    box[2] = r + area[0];
    box[1] = area[1];
    box[3] = r + area[1];
    if (open_cfw_lv_area_is_point_on(box, point, 0)) {
        box[2] = box[2] + r;
        box[3] = box[3] + r;
        return open_cfw_lv_area_point_within_corner_radius(box, point);
    }

    /* Bottom-left corner square. */
    box[1] = area[3] - r;
    box[3] = area[3];
    if (open_cfw_lv_area_is_point_on(box, point, 0)) {
        box[2] = box[2] + r;
        box[1] = box[1] - r;
        return open_cfw_lv_area_point_within_corner_radius(box, point);
    }

    /* Bottom-right corner square. */
    box[0] = area[2] - r;
    box[2] = area[2];
    if (open_cfw_lv_area_is_point_on(box, point, 0)) {
        box[0] = box[0] - r;
        box[1] = box[1] - r;
        return open_cfw_lv_area_point_within_corner_radius(box, point);
    }

    /* Top-right corner square. */
    box[1] = area[1];
    box[3] = r + area[1];
    if (open_cfw_lv_area_is_point_on(box, point, 0)) {
        box[0] = box[0] - r;
        box[3] = box[3] + r;
        return open_cfw_lv_area_point_within_corner_radius(box, point);
    }

    return 1;
}

__attribute__((used, noinline))
int open_cfw_lv_area_is_on(const int *a1, const int *a2)
{
    if (a2[2] < a1[0] || a1[2] < a2[0] || a2[3] < a1[1] || a1[3] < a2[1]) {
        return 0;
    }
    return 1;
}

__attribute__((used, noinline))
int open_cfw_lv_area_is_in(const int *ain, const int *aholder, int radius)
{
    int fits =
        (aholder[0] <= ain[0]) && (aholder[1] <= ain[1]) &&
        (ain[2] <= aholder[2]) && (ain[3] <= aholder[3]);
    int corner[2];

    if (!fits) {
        return 0;
    }
    if (radius == 0) {
        return 1;
    }

    corner[0] = ain[0]; corner[1] = ain[1];
    if (!open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = ain[2]; corner[1] = ain[1];
    if (!open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = ain[0]; corner[1] = ain[3];
    if (!open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = ain[2]; corner[1] = ain[3];
    if (!open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    return 1;
}

__attribute__((used, noinline))
int open_cfw_lv_area_is_out(const int *aout, const int *aholder, int radius)
{
    int corner[2];

    if (aout[2] < aholder[0] || aout[3] < aholder[1] ||
        aholder[2] < aout[0] || aholder[3] < aout[1]) {
        return 1;
    }
    if (radius == 0) {
        return 0;
    }

    corner[0] = aout[0]; corner[1] = aout[1];
    if (open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = aout[2]; corner[1] = aout[1];
    if (open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = aout[0]; corner[1] = aout[3];
    if (open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    corner[0] = aout[2]; corner[1] = aout[3];
    if (open_cfw_lv_area_is_point_on(aholder, corner, radius)) {
        return 0;
    }
    return 1;
}

/*
 * FUN_00450c2a.  Splits off up to four rectangles of `a1` that remain after
 * removing the part shared with `a2`: a strip above a2's top edge, a strip
 * below a2's bottom edge, then (within the vertical band both areas share) a
 * strip left of a2's left edge and a strip right of a2's right edge.  `res`
 * must have room for 4 areas (16 ints).
 */
__attribute__((used, noinline))
int open_cfw_lv_area_diff(int *res, const int *a1, const int *a2)
{
    int count = 0;
    int max_y1;
    int min_y2;
    int overlap_height;

    if (!open_cfw_lv_area_is_on(a1, a2)) {
        return -1;
    }
    if (open_cfw_lv_area_is_in(a1, a2, 0)) {
        return 0;
    }

    max_y1 = (a1[1] < a2[1]) ? a2[1] : a1[1];
    min_y2 = (a2[3] < a1[3]) ? a2[3] : a1[3];
    overlap_height = min_y2 - max_y1;

    if (a2[1] > a1[1]) {
        res[count * 4 + 0] = a1[0];
        res[count * 4 + 1] = a1[1];
        res[count * 4 + 2] = a1[2];
        res[count * 4 + 3] = a2[1] - 1;
        count++;
    }

    if (a1[3] > a2[3]) {
        res[count * 4 + 0] = a1[0];
        res[count * 4 + 1] = a2[3] + 1;
        res[count * 4 + 2] = a1[2];
        res[count * 4 + 3] = a1[3];
        count++;
    }

    if (a2[0] > a1[0] && overlap_height > 0) {
        res[count * 4 + 0] = a1[0];
        res[count * 4 + 1] = max_y1;
        res[count * 4 + 2] = a2[0] - 1;
        res[count * 4 + 3] = min_y2;
        count++;
    }

    if (a1[2] > a2[2]) {
        res[count * 4 + 0] = a2[2] + 1;
        res[count * 4 + 1] = max_y1;
        res[count * 4 + 2] = a1[2];
        res[count * 4 + 3] = min_y2;
        count++;
    }

    return count;
}

/*
 * FUN_00451082.  Positions `to_align` relative to `base` per the LVGL
 * `lv_align_t` table (LV_ALIGN_TOP_LEFT=1 .. LV_ALIGN_OUT_RIGHT_BOTTOM=21;
 * 0 or out of range keeps the LV_ALIGN_DEFAULT offset of {0, 0}), then adds
 * `ofs_x`/`ofs_y` and rewrites `to_align` in place, preserving its original
 * width/height.  Stock IAR codegen recomputed width/height per switch case
 * (and again for to_align after the switch); this reviewed C caches all
 * four metrics once up front, which is arithmetically identical since
 * nothing here mutates `base` or `to_align` before they are read.
 */
__attribute__((used, noinline))
void open_cfw_lv_area_align(
    const int *base,
    int *to_align,
    int align,
    int ofs_x,
    int ofs_y
)
{
    int base_w = open_cfw_lv_area_get_width(base);
    int base_h = open_cfw_lv_area_get_height(base);
    int align_w = open_cfw_lv_area_get_width(to_align);
    int align_h = open_cfw_lv_area_get_height(to_align);
    int dx;
    int dy;

    switch (align) {
    case 1: dx = 0; dy = 0; break;
    case 2: dx = base_w / 2 - align_w / 2; dy = 0; break;
    case 3: dx = base_w - align_w; dy = 0; break;
    case 4: dx = 0; dy = base_h - align_h; break;
    case 5: dx = base_w / 2 - align_w / 2; dy = base_h - align_h; break;
    case 6: dx = base_w - align_w; dy = base_h - align_h; break;
    case 7: dx = 0; dy = base_h / 2 - align_h / 2; break;
    case 8: dx = base_w - align_w; dy = base_h / 2 - align_h / 2; break;
    case 9: dx = base_w / 2 - align_w / 2; dy = base_h / 2 - align_h / 2; break;
    case 10: dx = 0; dy = -align_h; break;
    case 11: dx = base_w / 2 - align_w / 2; dy = -align_h; break;
    case 12: dx = base_w - align_w; dy = -align_h; break;
    case 13: dx = 0; dy = base_h; break;
    case 14: dx = base_w / 2 - align_w / 2; dy = base_h; break;
    case 15: dx = base_w - align_w; dy = base_h; break;
    case 16: dx = -align_w; dy = 0; break;
    case 17: dx = -align_w; dy = base_h / 2 - align_h / 2; break;
    case 18: dx = -align_w; dy = base_h - align_h; break;
    case 19: dx = base_w; dy = 0; break;
    case 20: dx = base_w; dy = base_h / 2 - align_h / 2; break;
    case 21: dx = base_w; dy = base_h - align_h; break;
    default: dx = 0; dy = 0; break;
    }

    to_align[0] = ofs_x + base[0] + dx;
    to_align[1] = ofs_y + base[1] + dy;
    to_align[2] = align_w + to_align[0] - 1;
    to_align[3] = align_h + to_align[1] - 1;
}
