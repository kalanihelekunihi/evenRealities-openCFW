
int Thread_BleMsgtxQueueClear(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  int iVar4;
  int local_18;
  undefined4 uStack_14;
  
  iVar1 = DAT_00475d70;
  iVar4 = 0;
  local_18 = 0;
  uStack_14 = in_r3;
  if (*(int *)(DAT_00475d70 + 0xc) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00475d6c,DAT_00475d68,DAT_00475ee8,0x10f,DAT_00475ee4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00475eec,DAT_00475eec);
    }
    iVar4 = 0;
  }
  else {
    uVar2 = osMessageQueueGetCount(*(undefined4 *)(DAT_00475d70 + 0xc));
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475ee8,0x114,DAT_00475ef0,uVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00475ef4,DAT_00475ef4,uVar2);
    }
    while ((iVar3 = osMessageQueueGet(*(undefined4 *)(iVar1 + 0xc),&local_18,0,0), iVar3 == 0 &&
           (local_18 != 0))) {
      file_heap_free(local_18);
      local_18 = 0;
      iVar4 = iVar4 + 1;
    }
    uVar2 = osMessageQueueGetCount(*(undefined4 *)(iVar1 + 0xc));
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475ee8,0x123,DAT_00475ef8,iVar4,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00475efc,DAT_00475efc,iVar4,uVar2);
    }
  }
  return iVar4;
}

