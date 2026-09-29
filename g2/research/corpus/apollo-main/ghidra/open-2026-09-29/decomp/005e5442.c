
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e5442(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = _DAT_005e5ed0;
  if ((*_DAT_005e5ed0 == 0) || (iVar2 = FUN_0043e2ea(*_DAT_005e5ed0), iVar2 == 0)) {
    FUN_005e5420(0);
  }
  else {
    FUN_0058c426(*piVar1,0xfa,PTR_FUN_005e5420_1_005e5ff4);
  }
  return 0;
}

