
void Write_CVT(int param_1,int param_2,undefined4 param_3)

{
  *(undefined4 *)(*(int *)(param_1 + 0x184) + param_2 * 4) = param_3;
  return;
}

