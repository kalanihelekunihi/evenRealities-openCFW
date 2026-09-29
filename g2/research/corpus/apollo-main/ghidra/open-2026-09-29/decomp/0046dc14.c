
undefined8
_blePsnIntoADV(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0xe3;
    param_3 = DAT_0046e014;
    param_4 = param_1;
    FUN_0043d574(4,DAT_0046dff8,DAT_0046dff4,DAT_0046e018,0xe3,DAT_0046e014,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046e01c,DAT_0046e01c,param_1,param_2,param_3,param_4);
  }
  uVar2 = FUN_0044a43c(param_1);
  FUN_00439be4(DAT_0046e020,param_1,uVar2);
  return CONCAT44(param_3,param_2);
}

