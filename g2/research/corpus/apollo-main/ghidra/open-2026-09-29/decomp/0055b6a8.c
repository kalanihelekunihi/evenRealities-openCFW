
longlong FUN_0055b6a8(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_18 = param_2;
  uStack_14 = param_3;
  uStack_10 = param_4;
  FUN_0043c0e4(&uStack_18,10,0);
  iVar1 = (**(code **)(DAT_0055ba00 + 4))(4,&uStack_18,10);
  if (iVar1 == 0) {
    FUN_00439be4(param_1,&uStack_18,10);
  }
  return (ulonglong)uStack_18 << 0x20;
}

