
void Ins_GFV(int param_1,int *param_2)

{
  *param_2 = (int)*(short *)(param_1 + 0x12e);
  param_2[1] = (int)*(short *)(param_1 + 0x130);
  return;
}

