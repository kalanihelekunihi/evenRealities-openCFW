/* SPDX-License-Identifier: MIT */
/* Recovered configuration of upstream lvp_audio_in.c buffer selection. */
extern unsigned int LvpGetMicBufferSize(void);
extern unsigned int LvpGetMicChannelNum(void);
extern unsigned int LvpGetLogfbankBufferSize(void);
extern void *LvpGetMicBufferAddr(void);
extern void *LvpGetLogfbankBufferAddr(void);
extern void *AudioInBoardGetParamCtrl(void);
unsigned int open_cfw_gx8002_audio_input_buffer_size(unsigned int channel)
{
    if (channel == 2) {
        unsigned int size = LvpGetMicBufferSize();
        return size / LvpGetMicChannelNum() * 2;
    }
    if (channel == 4)
        return LvpGetLogfbankBufferSize();
    return 0;
}
void *open_cfw_gx8002_audio_input_buffer_addr(unsigned int channel)
{
    (void)AudioInBoardGetParamCtrl();
    if (channel == 1 || channel == 2)
        return LvpGetMicBufferAddr();
    if (channel == 4)
        return LvpGetLogfbankBufferAddr();
    return (void *)0;
}
