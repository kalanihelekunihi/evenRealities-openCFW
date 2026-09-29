
undefined8 _bleSlaveSecReq(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar2 = 0x138;
    param_2 = DAT_0046e088;
    FUN_0043d574(4,DAT_0046dff8,DAT_0046dff4,DAT_0046e08c,0x138,DAT_0046e088,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046e090,DAT_0046e090,param_1 & 0xff,uVar2,param_2,param_3);
  }
  FUN_004b4684(param_1 & 0xff);
  return CONCAT44(param_2,uVar2);
}

