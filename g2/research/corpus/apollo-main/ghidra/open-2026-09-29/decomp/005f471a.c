
void Current_Ppem_Stretched(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = Current_Ratio(param_1);
  FT_MulFix(*(undefined2 *)(param_1 + 0x100),uVar1);
  return;
}

