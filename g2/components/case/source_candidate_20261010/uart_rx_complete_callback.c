#include "../frame_callback_offline/frame.h"

/* Stock RX8/RX16 completion calls original product parser 0x08006544.
 * The source parser owns that body; this public HAL name binds its ABI. */
void HAL_UART_RxCpltCallback(case_start_handle *uart)
{
    case_frame_callback(uart);
}
