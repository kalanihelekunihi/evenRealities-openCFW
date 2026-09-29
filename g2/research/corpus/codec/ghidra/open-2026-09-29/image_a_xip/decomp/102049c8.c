
void aout_set_r1_frame_over_int_enable(int param_1,uint param_2)

{
  *(uint *)(param_1 + 8) = (param_2 & 1) << 1 | *(uint *)(param_1 + 8) & 0xfffffffd;
  return;
}

