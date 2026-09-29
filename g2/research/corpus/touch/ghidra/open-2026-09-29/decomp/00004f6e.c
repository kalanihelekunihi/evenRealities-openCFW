
void touch_record_1c6e_history_filter(int param_1,ushort *param_2,ushort *param_3)

{
  ushort uVar1;
  
  if ((*(ushort *)(param_1 + 0x74) & 0x1800) == 0x1000) {
    uVar1 = (ushort)((uint)*param_2 + (uint)*param_3 + (uint)param_3[1] + (uint)param_3[2] >> 2);
    param_3[2] = param_3[1];
    param_3[1] = *param_3;
  }
  else {
    uVar1 = (ushort)((uint)*param_2 + (uint)*param_3 >> 1);
  }
  *param_3 = *param_2;
  *param_2 = uVar1;
  return;
}

