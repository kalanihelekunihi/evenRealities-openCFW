/* Native WsfTaskLock/Unlock 0x52b8c8/0x52b8d0. */
extern void audio_wsf_cs_enter(void);
extern void audio_wsf_cs_exit(void);
void WsfTaskLock(void) { audio_wsf_cs_enter(); }
void WsfTaskUnlock(void) { audio_wsf_cs_exit(); }
