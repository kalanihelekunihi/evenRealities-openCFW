
undefined8 ring_task_msg_send(undefined4 param_1,int param_2,ushort param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *local_20;
  
  iVar1 = DAT_004c5648;
  local_20 = param_4;
  if ((param_2 == 0) && (param_3 != 0)) {
    iVar1 = FUN_0043d0ce();
    iVar4 = param_2;
    if (iVar1 << 0x1e < 0) {
      iVar4 = 0x182;
      FUN_0043d574(1,DAT_004c5640,DAT_004c563c,DAT_004c5714,0x182,DAT_004c5710);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004c5718,DAT_004c5718);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(int *)(DAT_004c5648 + 0xc) == 0) {
    iVar1 = FUN_0043d0ce();
    iVar4 = param_2;
    if (iVar1 << 0x1e < 0) {
      iVar4 = 0x187;
      FUN_0043d574(1,DAT_004c5640,DAT_004c563c,DAT_004c5714,0x187,DAT_004c571c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004c5720,DAT_004c5720);
    }
    uVar2 = 0xffffffff;
  }
  else {
    local_20 = (undefined4 *)0x0;
    iVar4 = param_2;
    local_20 = (undefined4 *)file_heap_allocate(param_3 + 8);
    if (local_20 == (undefined4 *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar4 = 399;
        FUN_0043d574(1,DAT_004c5640,DAT_004c563c,DAT_004c5714,399,DAT_004c5724);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004c5728,DAT_004c5728);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = 0;
      FUN_0043c0e4(local_20,8,0);
      *local_20 = param_1;
      local_20[1] = (uint)param_3;
      if ((param_3 != 0) && (param_2 != 0)) {
        FUN_00439be4(local_20 + 2,param_2,param_3);
      }
      iVar3 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),&local_20,0,0);
      if (iVar3 == 0) {
        osThreadFlagsSet(*(undefined4 *)(iVar1 + 8),0x400000);
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar4 = 0x19c;
          FUN_0043d574(1,DAT_004c5640,DAT_004c563c,DAT_004c5714,0x19c,DAT_004c572c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004c5730,DAT_004c5730);
        }
        file_heap_free(local_20);
        uVar2 = 0xffffffff;
      }
    }
  }
  return CONCAT44(iVar4,uVar2);
}

