
void gx8002_tws_done(void)

{
  gx8002_memset(DAT_10208668,0,0x14);
  LvpKwsDone();
  LvpAudioInDone();
  gx8002_printf(PTR_s__LVP_TWS_Exit_TWS_mode_1020866c);
  return;
}

