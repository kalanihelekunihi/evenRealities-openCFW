
undefined8 Thread_MsgPbTxByBleDirect(undefined1 param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = param_2;
  uVar4 = param_4;
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    uVar2 = Thread_MsgTxByBle(0,0,param_1,param_2 & 0xff,param_3,param_4 & 0xffff,uVar4);
  }
  else {
    iVar1 = FUN_0043d0ce();
    param_3 = uVar3;
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x198;
      FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475f48,0x198,DAT_00475f44);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00475f4c,DAT_00475f4c);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

