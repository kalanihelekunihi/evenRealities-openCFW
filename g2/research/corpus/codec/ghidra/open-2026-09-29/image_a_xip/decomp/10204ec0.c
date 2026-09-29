
undefined4 gx8002_aout_suspend(int param_1)

{
  if (*(char *)(param_1 + 0x1b) != '\0') {
    uRam00000008 = uRam00000008 & 0xfffffffe;
    uRam0000000c = uRam0000000c & 1;
  }
  if (*(char *)(param_1 + 0x1a) != '\0') {
    aout_play_check_idle(0,0);
    aout_set_r1_frame_over_int_enable(0,0);
    uRam0000000c = uRam0000000c & 2;
  }
  func_0x10025080(0xb,0);
  func_0x10025080(0xf,0);
  return 0;
}

