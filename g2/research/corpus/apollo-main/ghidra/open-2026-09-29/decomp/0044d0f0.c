
undefined4
FUN_0044d0f0(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (param_1 != (undefined4 *)0x0) {
    FUN_0043f648(param_1);
    FUN_0044bde0(0);
    FUN_00482f8a(param_1);
    FUN_0044d1fc(*param_1,param_1);
    FUN_0044bde0(1);
    FUN_0044bc8c(param_1,0xf0000,0xff);
    FUN_0043ffa0(param_1);
    iVar1 = FUN_0044d33a();
    if ((iVar1 != 0) && (iVar2 = FUN_0044d1cc(param_1), iVar2 != 0)) {
      FUN_0044d342(iVar1,param_1);
    }
    iVar1 = FUN_0044dca2(param_1);
    if (iVar1 != 0) {
      FUN_00451670(iVar1,0x2a,param_1);
      FUN_00451670(iVar1,0x2b,param_1);
      FUN_00440656(param_1);
    }
  }
  return param_4;
}

