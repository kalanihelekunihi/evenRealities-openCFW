
void aout_play_check_idle(uint *param_1,uint param_2)

{
  *param_1 = (param_2 & 1) << 1 | *param_1 & 0xfffffffd;
  return;
}

