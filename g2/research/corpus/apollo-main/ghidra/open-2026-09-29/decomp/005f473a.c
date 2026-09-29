
void Read_CVT_Stretched(int param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = Current_Ratio(param_1);
  FT_MulFix(*(undefined4 *)(*(int *)(param_1 + 0x184) + param_2 * 4),uVar1);
  return;
}

