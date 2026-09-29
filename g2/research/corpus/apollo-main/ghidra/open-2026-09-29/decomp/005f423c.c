
void TT_Set_CodeRange(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined4 *)(param_1 + param_2 * 8 + 0x1b8) = param_3;
  *(undefined4 *)(param_1 + param_2 * 8 + 0x1bc) = param_4;
  return;
}

