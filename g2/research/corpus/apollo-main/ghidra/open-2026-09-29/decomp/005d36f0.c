
int FUN_005d36f0(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  if ((*(int *)(param_1 + 0x14) == 0) || (*(char *)(param_1 + 0xd) == '\0')) {
    iVar1 = FT_MulFix(param_2,*(undefined4 *)(param_1 + 0x10));
  }
  else {
    uVar2 = *(uint *)(param_1 + 0x18);
    while ((uVar2 < *(int *)(param_1 + 0x14) - 1U &&
           (*(int *)(uVar2 * 0x14 + param_1 + 0x38) <= param_2))) {
      uVar2 = uVar2 + 1;
    }
    while ((uVar2 != 0 && (param_2 < *(int *)(uVar2 * 0x14 + param_1 + 0x24)))) {
      uVar2 = uVar2 - 1;
    }
    *(uint *)(param_1 + 0x18) = uVar2;
    if ((uVar2 == 0) && (param_2 < *(int *)(param_1 + 0x24))) {
      iVar1 = FT_MulFix(param_2 - *(int *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x10));
      iVar1 = *(int *)(param_1 + 0x28) + iVar1;
    }
    else {
      iVar1 = FT_MulFix(param_2 - *(int *)(uVar2 * 0x14 + param_1 + 0x24),
                        *(undefined4 *)(uVar2 * 0x14 + param_1 + 0x2c));
      iVar1 = *(int *)(param_1 + uVar2 * 0x14 + 0x28) + iVar1;
    }
  }
  return iVar1;
}

