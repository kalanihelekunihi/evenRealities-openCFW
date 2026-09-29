
undefined8 GattDiscover(undefined1 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_4 = (uint)*DAT_004b5abc;
    uVar2 = 0x67;
    param_3 = DAT_004b5ac0;
    FUN_0043d574(4,DAT_004b5acc,DAT_004b5ac8,DAT_004b5ac4,0x67,DAT_004b5ac0,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004b5ad0,DAT_004b5ad0,*DAT_004b5abc,uVar2,param_3,param_4);
  }
  uVar2 = DAT_004b5ad4;
  FUN_005332b4(param_1,2,DAT_004b5abc,2);
  return CONCAT44(param_2,uVar2);
}

