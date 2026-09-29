
void touch_record_2620_threshold_delta(int param_1,ushort *param_2)

{
  param_2[2] = 0;
  if ((uint)param_2[1] + (uint)*(ushort *)(param_1 + 0x1a) < (uint)*param_2) {
    param_2[2] = *param_2 - param_2[1];
  }
  return;
}

