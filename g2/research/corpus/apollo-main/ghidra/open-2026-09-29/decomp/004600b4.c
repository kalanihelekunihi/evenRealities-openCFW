
undefined4 FUN_004600b4(undefined4 param_1)

{
  int *piVar1;
  int iVar2;
  ushort uVar3;
  
  piVar1 = DAT_00460120;
  if (*DAT_00460120 != 0) {
    uVar3 = 0;
    while (*(int *)(*piVar1 + (uint)uVar3 * 4) != 0) {
      iVar2 = FUN_0046cacc(**(undefined4 **)(*piVar1 + (uint)uVar3 * 4),param_1);
      if (iVar2 == 0) {
        *DAT_0046011c = *(undefined4 *)(*piVar1 + (uint)uVar3 * 4);
        return 0;
      }
      uVar3 = uVar3 + 1;
    }
  }
  return 0xffffffff;
}

