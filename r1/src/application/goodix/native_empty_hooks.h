/* Native register-hook position 3 points to 0x6a4fe.
 * It is a single return through LR. The public template's FIFO monitor
 * action is absent from this R1 hook.
 */
#ifndef R1_NATIVE_EMPTY_HOOKS_H
#define R1_NATIVE_EMPTY_HOOKS_H
void gh3x2x_get_rawdata_hook_func(GU8 *buffer, GU16 length)
{
    (void)buffer;
    (void)length;
}
#endif
