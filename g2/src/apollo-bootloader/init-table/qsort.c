/* SPDX-License-Identifier: MIT
 * Source implementation of the stock introspective qsort used by the boot
 * initializer. The executable entry is a component API, not a vendored blob.
 */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t (*sort_compare_fn)(const void *, const void *);

static unsigned char *at(unsigned char *base, uint32_t index, uint32_t width)
{
    return base + (uintptr_t)index * width;
}

static void swap_item(unsigned char *left, unsigned char *right,
                      uint32_t width)
{
    if (width < 64u) {
        for (uint32_t i = 0; i < width; ++i) {
            unsigned char byte = left[i];
            left[i] = right[i];
            right[i] = byte;
        }
    } else {
        unsigned char scratch[128];
        while (width != 0u) {
            const uint32_t chunk = width < sizeof(scratch) ? width : sizeof(scratch);
            for (uint32_t i = 0; i < chunk; ++i)
                scratch[i] = left[i];
            for (uint32_t i = 0; i < chunk; ++i)
                left[i] = right[i];
            for (uint32_t i = 0; i < chunk; ++i)
                right[i] = scratch[i];
            left += chunk;
            right += chunk;
            width -= chunk;
        }
    }
}

static void rotate3(unsigned char *a, unsigned char *b, unsigned char *c,
                    uint32_t width)
{
    if (width < 64u) {
        for (uint32_t i = 0; i < width; ++i) {
            unsigned char saved = a[i];
            a[i] = c[i];
            c[i] = b[i];
            b[i] = saved;
        }
    } else {
        unsigned char scratch[128];
        while (width != 0u) {
            const uint32_t chunk = width < sizeof(scratch) ? width : sizeof(scratch);
            for (uint32_t i = 0; i < chunk; ++i)
                scratch[i] = a[i];
            for (uint32_t i = 0; i < chunk; ++i)
                a[i] = c[i];
            for (uint32_t i = 0; i < chunk; ++i)
                c[i] = b[i];
            for (uint32_t i = 0; i < chunk; ++i)
                b[i] = scratch[i];
            a += chunk;
            b += chunk;
            c += chunk;
            width -= chunk;
        }
    }
}

static void median3(unsigned char *base, uint32_t a, uint32_t b, uint32_t c,
                    uint32_t width, sort_compare_fn compare)
{
    unsigned char *pa = at(base, a, width);
    unsigned char *pb = at(base, b, width);
    unsigned char *pc = at(base, c, width);
    if (compare(pb, pa) < 0)
        swap_item(pa, pb, width);
    if (compare(pc, pb) < 0)
        swap_item(pb, pc, width);
    if (compare(pb, pa) < 0)
        swap_item(pa, pb, width);
}

static void sift_down(unsigned char *base, uint32_t root, uint32_t count,
                      uint32_t width, sort_compare_fn compare)
{
    while (root < count / 2u) {
        uint32_t child = root * 2u + 1u;
        if (child + 1u < count &&
            compare(at(base, child, width), at(base, child + 1u, width)) < 0)
            ++child;
        if (compare(at(base, root, width), at(base, child, width)) >= 0)
            return;
        swap_item(at(base, root, width), at(base, child, width), width);
        root = child;
    }
}

static void heap_sort(unsigned char *base, uint32_t count, uint32_t width,
                      sort_compare_fn compare)
{
    for (uint32_t i = count / 2u; i > 0u; --i)
        sift_down(base, i - 1u, count, width, compare);
    for (uint32_t end = count; end > 1u; --end) {
        swap_item(base, at(base, end - 1u, width), width);
        sift_down(base, 0u, end - 1u, width, compare);
    }
}

static void insertion_sort(unsigned char *base, uint32_t count,
                           uint32_t width, sort_compare_fn compare)
{
    for (uint32_t i = 1u; i < count; ++i) {
        unsigned char *const current = at(base, i, width);
        uint32_t target = i;
        /* Native small-sort first compares against the first record, then
         * scans backward. This includes a second comparison at count two
         * when the first comparison is nonnegative. */
        if (compare(current, base) < 0)
            target = 0u;
        else {
            for (uint32_t scan = i; scan > 0u; --scan) {
                if (compare(current, at(base, scan - 1u, width)) < 0)
                    target = scan - 1u;
                else
                    break;
            }
        }
        for (uint32_t j = i; j > target; --j)
            swap_item(at(base, j, width), at(base, j - 1u, width), width);
    }
}

/* Stock 0x423A48 (qsort_introsort_core; IAR DLIB qsort core) */
static void intro_sort(unsigned char *base, uint32_t count, uint32_t width,
                       uint32_t budget, sort_compare_fn compare)
{
    for (;;) {
        if (count < 2u)
            return;
        if (budget == 0u) {
            heap_sort(base, count, width, compare);
            return;
        }
        if (count < 33u) {
            insertion_sort(base, count, width, compare);
            return;
        }

        uint32_t middle = count / 2u;
        uint32_t last = count - 1u;
        if (count > 41u) {
            uint32_t step = (last >> 3) + 1u;
            median3(base, 0u, step, 2u * step, width, compare);
            median3(base, middle - step, middle, middle + step,
                    width, compare);
            median3(base, last - 2u * step, last - step, last,
                    width, compare);
            median3(base, step, middle, last - step, width, compare);
        } else {
            median3(base, 0u, middle, last, width, compare);
        }

        /* The native core compares against the live middle record before
         * partitioning; it does not allocate a width-sized pivot copy. */
        unsigned char *pivot = at(base, middle, width);

        /* The stock code recognizes the all-equal case without permuting it. */
        uint32_t equal_left = middle;
        while (equal_left > 0u &&
               compare(at(base, equal_left - 1u, width), pivot) == 0)
            --equal_left;
        uint32_t equal_right = middle + 1u;
        while (equal_right < count &&
               compare(at(base, equal_right, width), pivot) == 0)
            ++equal_right;
        if (equal_left == 0u && equal_right == count)
            return;

        /* The original partition keeps the pivot at `middle`, the right
         * equal band at [pivot+1,right_equal), and scans the remaining right
         * side forward. `left_cursor` mirrors stock sl at 0x423b56: it moves
         * left over low values and collects equal values next to the pivot.
         */
        uint32_t right_equal = middle + 1u;
        uint32_t right_scan = right_equal;
        uint32_t left_cursor = middle;
        uint32_t partition_pivot = middle;
        for (;;) {
            /* 0x423af8..0x423b16: greater values pass, equals join the
             * right equal band, and a lesser value starts the left scan. */
            while (right_scan < count) {
                int32_t order = compare(at(base, partition_pivot, width),
                                       at(base, right_scan, width));
                if (order < 0) {
                    ++right_scan;
                    continue;
                }
                if (order == 0) {
                    swap_item(at(base, right_equal, width),
                              at(base, right_scan, width), width);
                    ++right_equal;
                    ++right_scan;
                    continue;
                }
                break;
            }

            /* 0x423b18..0x423b98: scan left. The original stores the
             * candidate in [sp+4], then moves sl only for low/equal values.
             */
            bool low_reached_base = false;
            bool found_high = false;
            while (left_cursor > 0u) {
                uint32_t candidate = left_cursor - 1u;
                int32_t order = compare(at(base, candidate, width),
                                        at(base, partition_pivot, width));
                if (order < 0) {
                    left_cursor = candidate;
                    if (left_cursor == 0u) {
                        low_reached_base = true;
                        break;
                    }
                    continue;
                }
                if (order == 0) {
                    --partition_pivot;
                    /* Native stores candidate in [sp+4] before the call;
                     * equal-band swap moves pivot but keeps that cursor. */
                    left_cursor = candidate;
                    swap_item(at(base, partition_pivot, width),
                              at(base, candidate, width), width);
                    if (left_cursor == 0u) {
                        low_reached_base = true;
                        break;
                    }
                    continue;
                }
                /* The stock cursor is still at its old position here; its
                 * 0x423b9a/0x423c1e path decrements sl before using candidate.
                 */
                found_high = true;
                break;
            }

            if (found_high && left_cursor != 0u) {
                uint32_t high = left_cursor - 1u;
                left_cursor = high;
                if (right_scan < count) {
                    swap_item(at(base, right_scan, width),
                              at(base, high, width), width);
                    ++right_scan;
                    continue;
                }
                --partition_pivot;
                --right_equal;
                if (high == partition_pivot)
                    swap_item(at(base, partition_pivot, width),
                              at(base, right_equal, width), width);
                else
                    rotate3(at(base, high, width),
                            at(base, right_equal, width),
                            at(base, partition_pivot, width), width);
                continue;
            }

            /* sl==base (0x423b9a): either rotate an equal pivot across the
             * remaining right item, or the partition is complete. */
            (void)low_reached_base;
            if (right_scan < count) {
                if (right_equal == right_scan)
                    swap_item(at(base, right_scan, width),
                              at(base, partition_pivot, width), width);
                else
                    rotate3(at(base, right_scan, width),
                            at(base, partition_pivot, width),
                            at(base, right_equal, width), width);
                ++right_scan;
                ++partition_pivot;
                ++right_equal;
                continue;
            }
            break;
        }

        uint32_t half = budget >> 1;
        uint32_t next_budget = half + (half >> 1);
        uint32_t left_count = partition_pivot;
        uint32_t right_count = count - right_equal;
        /* Native branches to the right-first path only when right<left;
         * equal partitions recurse left first. */
        if (left_count <= right_count) {
            intro_sort(base, left_count, width, next_budget, compare);
            base = at(base, right_equal, width);
            count = right_count;
        } else {
            intro_sort(at(base, right_equal, width), right_count, width,
                       next_budget, compare);
            count = left_count;
        }
        budget = next_budget;
    }
}

/* Stock 0x423D08 (qsort_public_wrapper; IAR DLIB qsort) */
void opencfw_boot_init_sort(
    void *array, uint32_t count, uint32_t width,
    int32_t (*compare)(const void *, const void *))
{
    /* Stock 0x423d08 guards only array and comparator pointers. The core
     * handles count<2; width zero still reaches its comparison path. */
    if (array == 0 || compare == 0)
        return;
    intro_sort((unsigned char *)array, count, width, count, compare);
}
