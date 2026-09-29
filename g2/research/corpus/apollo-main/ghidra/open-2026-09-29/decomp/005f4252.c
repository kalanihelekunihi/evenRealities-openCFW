
void TT_Clear_CodeRange(int param_1,int param_2)

{
  *(undefined4 *)(param_1 + param_2 * 8 + 0x1b8) = 0;
  *(undefined4 *)(param_1 + param_2 * 8 + 0x1bc) = 0;
  return;
}

