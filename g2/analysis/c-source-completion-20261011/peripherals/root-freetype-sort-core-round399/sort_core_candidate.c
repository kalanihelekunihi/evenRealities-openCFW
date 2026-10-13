#include <stdint.h>

typedef int32_t (*ft_sort_compare)(const void *, const void *);
extern void audio_uart_ft_sort_swap_5677a8(uint8_t *, uint8_t *, uint32_t);
extern void audio_uart_ft_sort_rotate_5677fe(uint8_t *, uint8_t *, uint8_t *, uint32_t);
extern void audio_uart_ft_sort_insert_56786c(uint8_t *, uint8_t *, uint32_t);
extern void audio_uart_ft_sort_median_5678b6(uint8_t *, uint8_t *, uint8_t *, uint32_t, ft_sort_compare);
extern uint32_t audio_uart_ft_sort_heap_sift_567906(uint8_t *, uint32_t, uint32_t, uint32_t, ft_sort_compare);

#define FT_PTR(x) ((uint8_t *)(uintptr_t)(x))
#define FT_CMP(a,b) compare(FT_PTR(a), FT_PTR(b))

/* Complete 0x56798c body candidate, pending all-path native qualification. */
void audio_uart_ft_sort_core_56798c(void *base, uint32_t count, uint32_t budget,
                                     uint32_t width, ft_sort_compare compare)
{
    uintptr_t current = (uintptr_t)base, left, pivot, end, right,
              scan, previous, first, scratch;
    uint32_t distance, result, chunk, local_budget = budget;
    int32_t relation;
    uint8_t swap_scratch[128];

    while ((first = current, local_budget != 0u && count > 32u)) {
        end = current + width * count;
        pivot = current + width * (count >> 1);
        previous = end - width;
        distance = (uint32_t)(previous - current) / width;
        right = pivot + width;
        left = pivot;
        if (distance > 40u) {
            uint32_t stride = width * ((distance >> 3) + 1u);
            audio_uart_ft_sort_median_5678b6(FT_PTR(current), FT_PTR(current + stride), FT_PTR(current + stride * 2u), width, compare);
            audio_uart_ft_sort_median_5678b6(FT_PTR(pivot - stride), FT_PTR(pivot), FT_PTR(pivot + stride), width, compare);
            audio_uart_ft_sort_median_5678b6(FT_PTR(previous - stride * 2u), FT_PTR(previous - stride), FT_PTR(previous), width, compare);
            first = current + stride;
            previous -= stride;
        }
        audio_uart_ft_sort_median_5678b6(FT_PTR(first), FT_PTR(pivot), FT_PTR(previous), width, compare);
        first = pivot;
        do {
            pivot = first;
            if (pivot <= current) break;
            relation = FT_CMP(pivot - width, pivot);
            first = pivot - width;
        } while (relation == 0);
        while ((first = right, left = pivot, right < end &&
                (relation = FT_CMP(right, pivot), relation == 0))) right += width;
scan_right:
        for (distance = width; right < end; right += width) {
            relation = FT_CMP(pivot, right);
            if (relation >= 0) {
                if (relation > 0) break;
                audio_uart_ft_sort_swap_5677a8(FT_PTR(first), FT_PTR(right), width);
                first += width;
            }
resume_right:
            ;
        }
        while ((width = distance, scan = left, scratch = current, current < scan)) {
            left = scan - width;
            relation = FT_CMP(left, pivot);
            distance = width;
            if (relation >= 0) {
                if (relation > 0) break;
                pivot -= width;
                scratch = left;
                scan = pivot;
                if (width < 64u) {
                    for (uint32_t i = 0; i < width; ++i) {
                        uint8_t t = FT_PTR(scan)[i];
                        FT_PTR(scan)[i] = FT_PTR(scratch)[i];
                        FT_PTR(scratch)[i] = t;
                    }
                } else {
                    uint32_t remaining = width;
                    do {
                        chunk = remaining > 128u ? 128u : remaining;
                        for (uint32_t i = 0; i < chunk; ++i) swap_scratch[i] = FT_PTR(scan)[i];
                        for (uint32_t i = 0; i < chunk; ++i) FT_PTR(scan)[i] = FT_PTR(scratch)[i];
                        for (uint32_t i = 0; i < chunk; ++i) FT_PTR(scratch)[i] = swap_scratch[i];
                        remaining -= chunk;
                        scan += chunk;
                        scratch += chunk;
                    } while (remaining != 0u);
                }
            }
        }
        if (scan != current) {
            left = scan - width;
            if (right != end) {
                audio_uart_ft_sort_swap_5677a8(FT_PTR(right), FT_PTR(left), width);
                goto resume_right;
            }
            pivot -= width;
            first -= width;
            if (left == pivot) audio_uart_ft_sort_swap_5677a8(FT_PTR(pivot), FT_PTR(first), width);
            else audio_uart_ft_sort_rotate_5677fe(FT_PTR(left), FT_PTR(first), FT_PTR(pivot), width);
            goto scan_right;
        }
        if (right != end) {
            if (first == right) audio_uart_ft_sort_swap_5677a8(FT_PTR(right), FT_PTR(pivot), width);
            else audio_uart_ft_sort_rotate_5677fe(FT_PTR(right), FT_PTR(pivot), FT_PTR(first), width);
            right += width;
            pivot += width;
            first += width;
            left = scan;
            goto scan_right;
        }
        local_budget = (local_budget >> 1) + (local_budget >> 2);
        count = (uint32_t)(pivot - scratch) / width;
        result = (uint32_t)(end - first) / width;
        if (result < count) {
            audio_uart_ft_sort_core_56798c(FT_PTR(first), result, local_budget, width, compare);
        } else {
            audio_uart_ft_sort_core_56798c(FT_PTR(current), count, local_budget, width, compare);
            count = result;
            current = first;
        }
    }
    if (count <= 32u) {
        if (count > 1u) {
            pivot = current;
insertion_next:
            count--;
            if (count != 0u) {
                pivot += width;
                relation = FT_CMP(pivot, first);
                right = first;
                end = pivot;
                if (relation >= 0) goto insertion_scan;
                goto insertion_move;
            }
        }
    } else {
        distance = count >> 1;
        while (distance != 0u) {
            distance--;
            audio_uart_ft_sort_heap_sift_567906(FT_PTR(first), distance, count, width, compare);
        }
        pivot = first + width * count;
        current = first;
        do {
            pivot -= width;
            audio_uart_ft_sort_swap_5677a8(FT_PTR(first), FT_PTR(pivot), width);
            count--;
            audio_uart_ft_sort_heap_sift_567906(FT_PTR(first), 0u, count, width, compare);
        } while (count > 1u);
    }
    return;
insertion_scan:
    do {
        right = end;
        relation = FT_CMP(pivot, right - width);
        end = right - width;
    } while (relation < 0);
    if (right != pivot) {
insertion_move:
        audio_uart_ft_sort_insert_56786c(FT_PTR(right), FT_PTR(pivot), width);
    }
    goto insertion_next;
}
