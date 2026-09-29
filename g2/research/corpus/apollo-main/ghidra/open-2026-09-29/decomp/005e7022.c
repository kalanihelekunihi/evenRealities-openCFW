
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e7022(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  
  iVar1 = _DAT_005e7268;
  if (*(int *)(_DAT_005e7268 + 4) != 0) {
    uVar3 = FUN_005e4f10(param_2);
    uVar2 = FUN_005e4f14(param_2);
    *(undefined1 *)(iVar1 + 0x28c) = uVar2;
    FUN_0044ea04(*(undefined4 *)(iVar1 + 4),uVar3,1);
  }
  return 0;
}

