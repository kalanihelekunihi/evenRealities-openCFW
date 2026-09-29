
undefined8 FUN_005b7aba(undefined4 *param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puStack_20;
  int iStack_1c;
  uint uStack_18;
  undefined4 uStack_14;
  
  puStack_20 = param_1;
  iStack_1c = param_2;
  if ((param_1 != (undefined4 *)0x0) && (param_2 != 0)) {
    *(char *)(param_1 + 2) = (char)param_3;
    *(char *)((int)param_1 + 9) = (char)param_4;
    *param_1 = 0;
    param_1[1] = 0;
    if ((param_3 & 0xff) != 0) {
      uStack_18 = param_3;
      uStack_14 = param_4;
      uVar1 = FUN_00498668(param_2);
      *param_1 = uVar1;
      FUN_0043f506(*param_1,0x18);
      FUN_0043f568(*param_1,0x18);
      FUN_0043ded4(*param_1,0x10000);
      FUN_0043dfa4(*param_1,0x10);
      FUN_005b8d20(param_1);
      uVar1 = FUN_00499416(param_2);
      param_1[1] = uVar1;
      FUN_0043f506(param_1[1],0x3fffffff);
      FUN_0043f568(param_1[1],0x3fffffff);
      FUN_0044143e(param_1[1],DAT_005b8860,0);
      FUN_0043c0e4(&puStack_20,0x10,0);
      FUN_005b8bc8(param_3 & 0xff,&puStack_20,0x10);
      FUN_0049942e(param_1[1],&puStack_20);
      FUN_005b7a4c(param_1);
    }
  }
  return CONCAT44(iStack_1c,puStack_20);
}

