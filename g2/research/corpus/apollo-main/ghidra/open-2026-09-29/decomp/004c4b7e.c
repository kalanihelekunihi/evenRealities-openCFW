
undefined4 APP_BleRingSendDataMsg(undefined4 param_1,undefined4 param_2,uint param_3,uint param_4)

{
  byte *pbVar1;
  undefined2 uVar2;
  int iVar3;
  ushort *puVar4;
  
  pbVar1 = DAT_004c4c68;
  if (((*DAT_004c4c68 == 0) || (*(int *)(DAT_004c4c68 + 4) == 0)) ||
     (**(short **)(DAT_004c4c68 + 4) == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      if (*(int *)(pbVar1 + 4) == 0) {
        param_4 = 0;
      }
      else {
        param_4 = (uint)**(ushort **)(pbVar1 + 4);
      }
      param_3 = (uint)*pbVar1;
      param_2 = DAT_004c4cd8;
      FUN_0043d574(2,DAT_004c4c78,DAT_004c4c74,DAT_004c4cdc,0x147,DAT_004c4cd8,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      if (*(int *)(pbVar1 + 4) == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = **(undefined2 **)(pbVar1 + 4);
      }
      compress_log_output(0x8800000,DAT_004c4ce0,DAT_004c4ce0,*pbVar1,uVar2,param_2,param_3,param_4)
      ;
    }
  }
  else {
    thread_ble_wsf_wait_tx_ready();
    puVar4 = (ushort *)WsfMsgAlloc(0xc);
    if (puVar4 == (ushort *)0x0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004c4c78,DAT_004c4c74,DAT_004c4cdc,0x153,DAT_004c4ce4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004c4ce8,DAT_004c4ce8);
      }
      thread_ble_wsf_tx_complete_notify();
    }
    else {
      *(undefined1 *)(puVar4 + 1) = 0xac;
      *puVar4 = (ushort)*pbVar1;
      *(undefined4 *)(puVar4 + 2) = param_1;
      puVar4[4] = (ushort)param_2;
      WsfMsgSend(pbVar1[1],puVar4);
    }
  }
  return 0;
}

