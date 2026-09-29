
undefined4 FUN_00597e54(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  while( true ) {
    iVar1 = DAT_00597e88;
    if (*DAT_00597e8c <= uVar3) {
      return 0;
    }
    iVar2 = FUN_0044b610(param_1,*(undefined4 *)(DAT_00597e88 + uVar3 * 4),0x18);
    if (iVar2 == 0) break;
    uVar3 = uVar3 + 1;
  }
  return *(undefined4 *)(iVar1 + uVar3 * 4);
}

