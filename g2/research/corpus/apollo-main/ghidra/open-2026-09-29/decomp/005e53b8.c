
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e53b8(void)

{
  int iVar1;
  
  iVar1 = DAT_005e5dd8;
  FUN_005e4c84(0);
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005e47fe(*(undefined4 *)(iVar1 + 0x1d0),_DAT_005e5ca8);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),_DAT_005e5ecc);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),PTR_s_Please_check_your_app__005e5ff0);
    FUN_005e4894();
  }
  return 0;
}

