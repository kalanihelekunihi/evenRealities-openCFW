
int Thread_BleMsgrxQueueClear(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  int iVar4;
  int local_18;
  undefined4 uStack_14;
  
  iVar1 = DAT_0048f324;
  iVar4 = 0;
  local_18 = 0;
  uStack_14 = in_r3;
  if (*(int *)(DAT_0048f324 + 0xc) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f360,0x11c,DAT_0048f35c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0048f364,DAT_0048f364);
    }
    iVar4 = 0;
  }
  else {
    uVar2 = osMessageQueueGetCount(*(undefined4 *)(DAT_0048f324 + 0xc));
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f360,0x121,DAT_0048f368,uVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0048f36c,DAT_0048f36c,uVar2);
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
      FUN_0043d574(4,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,DAT_0048f360,0x130,DAT_0048f370,iVar4,
                   uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0048f374,DAT_0048f374,iVar4,uVar2);
    }
  }
  return iVar4;
}

