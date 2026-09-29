
undefined4 FUN_00597c6c(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    if (param_2 <= uVar2) {
      return 0;
    }
    iVar1 = FUN_00597e54(uVar2 * 0x40 + param_1 + 0x1c);
    if (iVar1 != 0) {
      if (*(int *)(iVar1 + 0x1c) <= *(int *)(uVar2 * 0x40 + param_1 + 0x34)) {
        *DAT_00597d20 = 0;
        return 0xffffffff;
      }
      *(int *)(DAT_00597d28 + uVar2 * 4) = iVar1;
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

