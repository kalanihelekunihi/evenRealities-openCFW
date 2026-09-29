
void touch_record_1ab8_reset(undefined2 *param_1)

{
  *(undefined1 *)(param_1 + 4) = 0;
  param_1[1] = *param_1;
  *(undefined1 *)((int)param_1 + 7) = 0;
  return;
}

