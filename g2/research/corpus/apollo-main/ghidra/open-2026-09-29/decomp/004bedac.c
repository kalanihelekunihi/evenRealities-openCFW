
undefined8
_anccSendCompleteNotificationMsg
          (undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0x17e;
    param_3 = DAT_004bf8b4;
    FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf8b8,0x17e,DAT_004bf8b4,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004bf8bc);
  }
  FUN_00464d1c(0x101,param_1,param_2 & 0xffff,DAT_004bf8c0);
  return CONCAT44(param_3,uVar2);
}

