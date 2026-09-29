
void tt_prepare_zone(int param_1,short *param_2,int param_3,int param_4)

{
  *(short *)(param_1 + 8) = param_2[1] - (short)param_3;
  *(short *)(param_1 + 10) = *param_2 - (short)param_4;
  *(int *)(param_1 + 0xc) = *(int *)(param_2 + 10) + param_3 * 8;
  *(int *)(param_1 + 0x10) = *(int *)(param_2 + 2) + param_3 * 8;
  *(int *)(param_1 + 0x14) = *(int *)(param_2 + 0xc) + param_3 * 8;
  *(int *)(param_1 + 0x18) = *(int *)(param_2 + 4) + param_3;
  *(int *)(param_1 + 0x1c) = *(int *)(param_2 + 6) + param_4 * 2;
  *(short *)(param_1 + 0x20) = (short)param_3;
  return;
}

