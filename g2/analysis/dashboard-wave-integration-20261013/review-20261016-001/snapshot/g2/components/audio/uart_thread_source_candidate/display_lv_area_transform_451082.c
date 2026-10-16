/* Apollo LV area alignment for modes 0..21, native 0x451082..0x4513ad. */
#include <stdint.h>

int32_t audio_uart_lv_area_transform_451082(const void *parent_area, void *child_area,
                                               uint8_t mode, int32_t offset_x,
                                               int32_t offset_y) {
    const int32_t *parent = (const int32_t *)parent_area;
    int32_t *child = (int32_t *)child_area;
    int32_t parent_width = parent[2] - parent[0] + 1;
    int32_t parent_height = parent[3] - parent[1] + 1;
    int32_t child_width = child[2] - child[0] + 1;
    int32_t child_height = child[3] - child[1] + 1;
    int32_t x = 0, y = 0;
    switch (mode) {
    case 2: x = parent_width / 2 - child_width / 2; break;
    case 3: x = parent_width - child_width; break;
    case 4: y = parent_height - child_height; break;
    case 5:
        x = parent_width / 2 - child_width / 2;
        y = parent_height - child_height;
        break;
    case 6:
        x = parent_width - child_width;
        y = parent_height - child_height;
        break;
    case 7: y = parent_height / 2 - child_height / 2; break;
    case 8:
        x = parent_width - child_width;
        y = parent_height / 2 - child_height / 2;
        break;
    case 9:
        x = parent_width / 2 - child_width / 2;
        y = parent_height / 2 - child_height / 2;
        break;
    case 10: y = -child_height; break;
    case 11:
        x = parent_width / 2 - child_width / 2;
        y = -child_height;
        break;
    case 12:
        x = parent_width - child_width;
        y = -child_height;
        break;
    case 13: y = parent_height; break;
    case 14:
        x = parent_width / 2 - child_width / 2;
        y = parent_height;
        break;
    case 15:
        x = parent_width - child_width;
        y = parent_height;
        break;
    case 16: x = -child_width; break;
    case 17:
        x = -child_width;
        y = parent_height / 2 - child_height / 2;
        break;
    case 18:
        x = -child_width;
        y = parent_height - child_height;
        break;
    case 19: x = parent_width; break;
    case 20:
        x = parent_width;
        y = parent_height / 2 - child_height / 2;
        break;
    case 21:
        x = parent_width;
        y = parent_height - child_height;
        break;
    default: break;
    }
    child[0] = offset_x + parent[0] + x;
    child[1] = offset_y + parent[1] + y;
    child[2] = child_width + child[0] - 1;
    child[3] = child_height + child[1] - 1;
    return offset_x;
}
