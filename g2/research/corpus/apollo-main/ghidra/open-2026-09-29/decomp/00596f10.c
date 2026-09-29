
longlong FUN_00596f10(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_0043c0e4(DAT_00597044,0x10,0);
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    uStack_10 = *(uint *)PTR_DAT_0059708c;
    uStack_c = *(undefined4 *)(PTR_DAT_0059708c + 4);
    FUN_0048eb32(DAT_00597080,2,&uStack_10);
  }
  FUN_0059ec28(8,0);
  return (ulonglong)uStack_10 << 0x20;
}

