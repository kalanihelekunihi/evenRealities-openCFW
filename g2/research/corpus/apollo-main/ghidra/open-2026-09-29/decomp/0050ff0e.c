
int FUN_0050ff0e(undefined4 param_1,byte param_2,byte param_3,undefined1 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0044cf98(DAT_0050ffc4,param_1);
  FUN_0044d0f0(iVar1);
  uVar2 = FUN_004515d2((uint)param_3 * 100);
  uVar3 = FUN_004515d2((uint)param_2 * 100);
  FUN_0043f09a(iVar1,uVar3,uVar2);
  *(undefined1 *)(iVar1 + 0x2c) = param_4;
  if (param_2 == 0 && param_3 == 0) {
    FUN_0044e3ca(param_1,param_4);
  }
  return iVar1;
}

