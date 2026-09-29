
longlong FUN_0058cf12(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_0043c0e4(DAT_0058d410,0x44,0);
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    uStack_10 = *(uint *)PTR_DAT_0058d494;
    uStack_c = *(undefined4 *)(PTR_DAT_0058d494 + 4);
    FUN_0048eb32(DAT_0058d498,2,&uStack_10);
  }
  FUN_00589b68(10,0);
  return (ulonglong)uStack_10 << 0x20;
}

