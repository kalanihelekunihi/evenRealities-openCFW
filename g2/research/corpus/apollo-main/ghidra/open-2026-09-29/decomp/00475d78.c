
undefined8
Thread_MsgStreamingNotifyByBle(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = param_2;
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    uVar2 = Thread_MsgTxByBle(1,1,0,0,param_1,param_2 & 0xffff,param_4);
  }
  else {
    iVar1 = FUN_0043d0ce();
    param_1 = uVar3;
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1e9;
      FUN_0043d574(4,DAT_00475f98,DAT_00475f94,DAT_00475fa0,0x1e9,DAT_00475f9c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00475fa4,DAT_00475fa4);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_1,uVar2);
}

