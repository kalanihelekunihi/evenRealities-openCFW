
void Ins_SSW(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = FT_MulFix(*param_2,*(undefined4 *)(param_1 + 0x108));
  *(undefined4 *)(param_1 + 0x14c) = uVar1;
  return;
}

