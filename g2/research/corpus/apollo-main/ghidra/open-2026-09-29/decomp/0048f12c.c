
undefined4 Thread_MsgRxFromBle(undefined4 param_1,int param_2,ushort param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *local_20;
  
  iVar1 = DAT_0048f324;
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f37c,0x13e,DAT_0048f378);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0048f380,DAT_0048f380);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(int *)(DAT_0048f324 + 0xc) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f37c,0x143,DAT_0048f384);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0048f388,DAT_0048f388);
    }
    uVar2 = 0xffffffff;
  }
  else {
    local_20 = (undefined4 *)0x0;
    local_20 = (undefined4 *)file_heap_allocate(param_3 + 0xb & 0xfffffffc);
    if (local_20 == (undefined4 *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f37c,0x14d,DAT_0048f38c,param_3
                    );
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0048f390,DAT_0048f390,param_3);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = 0;
      FUN_0043c0e4(local_20 + 2,param_3,0);
      *local_20 = param_1;
      local_20[1] = (uint)param_3;
      FUN_00439be4(local_20 + 2,param_2,param_3);
      uVar3 = osMessageQueueGetCount(*(undefined4 *)(iVar1 + 0xc));
      uVar4 = osMessageQueueGetCapacity(*(undefined4 *)(iVar1 + 0xc));
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f37c,0x15d,DAT_0048f394,uVar3,
                     uVar4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_0048f398,DAT_0048f398,uVar3,uVar4);
      }
      iVar5 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),&local_20,0,500);
      if (iVar5 == 0) {
        osThreadFlagsSet(*(undefined4 *)(iVar1 + 8),0x400000);
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f37c,0x160,DAT_0048f39c,iVar5
                      );
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0048f3a0,DAT_0048f3a0,iVar5);
        }
        file_heap_free(local_20);
        uVar2 = 0xffffffff;
      }
    }
  }
  return uVar2;
}

