
undefined4
Thread_MsgTxByBle(byte param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4,int param_5,
                 ushort param_6)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined4 *local_28;
  
  iVar1 = DAT_00475d70;
  if (param_5 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x131,DAT_00475f00);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00475f08,DAT_00475f08);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(int *)(DAT_00475d70 + 0xc) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x136,DAT_00475f0c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00475f10,DAT_00475f10);
    }
    uVar2 = 0xffffffff;
  }
  else {
    if ((param_1 == 1) && (iVar3 = ble_msgtx_isConnected(), iVar3 == 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x13b,DAT_00475f14);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00475f18,DAT_00475f18);
      }
      APP_ConnectParamESSSetFastMode();
    }
    local_28 = (undefined4 *)0x0;
    local_28 = (undefined4 *)file_heap_allocate(param_6 + 0xe & 0xfffffffc);
    if (local_28 == (undefined4 *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x144,DAT_00475f1c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00475f20,DAT_00475f20);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = 0;
      if (param_1 == 0) {
        *local_28 = 1;
        local_28[1] = param_6 + 3;
        *(undefined1 *)(local_28 + 2) = param_2;
        *(undefined1 *)((int)local_28 + 9) = param_3;
        *(undefined1 *)((int)local_28 + 10) = param_4;
        FUN_00439be4((int)local_28 + 0xb,param_5,param_6);
      }
      else if (param_1 == 2) {
        *local_28 = 4;
        local_28[1] = param_6 + 3;
        *(undefined1 *)(local_28 + 2) = param_2;
        *(undefined1 *)((int)local_28 + 9) = param_3;
        *(undefined1 *)((int)local_28 + 10) = param_4;
        FUN_00439be4((int)local_28 + 0xb,param_5,param_6);
      }
      else if (param_1 < 2) {
        *local_28 = 2;
        local_28[1] = (uint)param_6;
        FUN_00439be4(local_28 + 2,param_5,param_6);
      }
      else if (param_1 == 3) {
        *local_28 = 8;
        local_28[1] = param_6 + 3;
        *(undefined1 *)(local_28 + 2) = param_2;
        *(undefined1 *)((int)local_28 + 9) = param_3;
        *(undefined1 *)((int)local_28 + 10) = param_4;
        FUN_00439be4((int)local_28 + 0xb,param_5,param_6);
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x173,DAT_00475f24,param_1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00475f28,DAT_00475f28,param_1);
        }
      }
      uVar4 = osMessageQueueGetCount(*(undefined4 *)(iVar1 + 0xc));
      uVar5 = osMessageQueueGetCapacity(*(undefined4 *)(iVar1 + 0xc));
      if (param_1 != 1) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x17b,DAT_00475f2c,uVar4,uVar5);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00475f30,DAT_00475f30,uVar4,uVar5);
        }
      }
      if ((param_1 == 1) && (uVar5 >> 1 <= uVar4)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x181,DAT_00475f34,uVar4,uVar5);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_00475f38,DAT_00475f38,uVar4,uVar5);
        }
        file_heap_free(local_28);
        uVar2 = 0;
      }
      else {
        iVar3 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),&local_28,0,500);
        if (iVar3 == 0) {
          osThreadFlagsSet(*(undefined4 *)(iVar1 + 8),0x400000);
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,DAT_00475f04,0x189,DAT_00475f3c,iVar3);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00475f40,DAT_00475f40,iVar3);
          }
          file_heap_free(local_28);
          uVar2 = 0xffffffff;
        }
      }
    }
  }
  return uVar2;
}

