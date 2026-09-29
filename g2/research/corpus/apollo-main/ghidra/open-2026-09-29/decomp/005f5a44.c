
void Ins_GPV(int param_1,int *param_2)

{
  *param_2 = (int)*(short *)(param_1 + 0x12a);
  param_2[1] = (int)*(short *)(param_1 + 300);
  return;
}

