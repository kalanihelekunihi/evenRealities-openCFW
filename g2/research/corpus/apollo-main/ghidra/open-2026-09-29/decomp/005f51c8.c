
void Ins_MINDEX(int param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *param_2;
  if ((iVar1 < 1) || (*(int *)(param_1 + 0x1c) < iVar1)) {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
  }
  else {
    uVar2 = *(undefined4 *)(*(int *)(param_1 + 0x18) + (*(int *)(param_1 + 0x1c) - iVar1) * 4);
    FUN_00439710(*(int *)(param_1 + 0x18) + (*(int *)(param_1 + 0x1c) - iVar1) * 4,
                 *(int *)(param_1 + 0x18) + (*(int *)(param_1 + 0x1c) - iVar1) * 4 + 4,
                 (iVar1 + -1) * 4);
    *(undefined4 *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4 + -4) = uVar2;
  }
  return;
}

