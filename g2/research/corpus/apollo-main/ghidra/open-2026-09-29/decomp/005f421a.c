
void TT_Goto_CodeRange(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = param_1 + param_2 * 8;
  *(undefined4 *)(param_1 + 0x168) = *(undefined4 *)(iVar1 + 0x1b8);
  *(undefined4 *)(param_1 + 0x170) = *(undefined4 *)(iVar1 + 0x1bc);
  *(undefined4 *)(param_1 + 0x16c) = param_3;
  *(int *)(param_1 + 0x164) = param_2;
  return;
}

