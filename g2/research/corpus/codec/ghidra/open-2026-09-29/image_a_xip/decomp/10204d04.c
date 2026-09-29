
undefined4 gx8002_aout_drain_frame(int param_1)

{
  *(undefined1 *)(param_1 + 0x1c) = 0;
  *(undefined1 *)(param_1 + 0x1a) = 1;
  aout_play_check_idle(0,1);
  aout_set_r1_frame_over_int_enable(0,1);
  while (*(char *)(param_1 + 0x1c) == '\0') {
    func_0x1002598c(1);
  }
  return 0;
}

