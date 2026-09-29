
undefined4 Ins_Goto_CodeRange(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 - 1U < 3) {
    iVar2 = param_1 + param_2 * 8;
    if (*(int *)(iVar2 + 0x1b8) == 0) {
      *(undefined4 *)(param_1 + 0xc) = 0x8a;
      uVar1 = 1;
    }
    else if (*(int *)(iVar2 + 0x1bc) < param_3) {
      *(undefined4 *)(param_1 + 0xc) = 0x83;
      uVar1 = 1;
    }
    else {
      *(int *)(param_1 + 0x168) = *(int *)(iVar2 + 0x1b8);
      *(undefined4 *)(param_1 + 0x170) = *(undefined4 *)(iVar2 + 0x1bc);
      *(int *)(param_1 + 0x16c) = param_3;
      *(int *)(param_1 + 0x164) = param_2;
      uVar1 = 0;
    }
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x84;
    uVar1 = 1;
  }
  return uVar1;
}

