
undefined8
PB_TxEncodeNotifyRingConnectInfo
          (ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 *puVar3;
  
  iVar1 = FUN_004b8122();
  if ((iVar1 == 0) || (*(char *)(iVar1 + 0x56) == '\0')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x1d4;
      FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb1c,0x1d4,DAT_004bcb18,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bcddc,DAT_004bcddc);
    }
    uVar2 = 0xffffffff;
  }
  else {
    puVar3 = (undefined2 *)WsfMsgAlloc(0xc);
    if (puVar3 == (undefined2 *)0x0) {
      uVar2 = 0xffffffff;
    }
    else {
      *(undefined1 *)(puVar3 + 1) = 0xbb;
      *puVar3 = 0;
      puVar3[4] = param_1 & 0xff;
      WsfMsgSend(*(undefined1 *)(iVar1 + 0x56),puVar3);
      uVar2 = 0;
    }
  }
  return CONCAT44(param_2,uVar2);
}

