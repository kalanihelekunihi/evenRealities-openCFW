
undefined4 navigation_send_type_1_allocating(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_40;
  undefined4 local_3c;
  uint local_34;
  undefined1 auStack_2c [20];
  
  puVar1 = (undefined1 *)file_heap_allocate(0x2024);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_3c = DAT_00586f04;
      local_40 = 0x4c;
      FUN_0043d574(1,DAT_00586f10,DAT_00586f0c,DAT_00586f08);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058704c,DAT_0058704c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = file_heap_allocate(10000);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_3c = DAT_00587050;
        local_40 = 0x53;
        FUN_0043d574(1,DAT_00586f10,DAT_00586f0c,DAT_00586f08);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00587054);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(puVar1,0x2024,0);
      FUN_0043c0e4(iVar2,10000,0);
      *puVar1 = 1;
      puVar1[1] = 0;
      *(undefined2 *)(puVar1 + 2) = 3;
      puVar1[4] = 0;
      FUN_004905f4(auStack_2c,iVar2,10000);
      FUN_00439c04(&local_40,auStack_2c,0x14);
      iVar4 = FUN_00490c32(&local_40,DAT_00587238,puVar1);
      if (iVar4 == 0) {
        file_heap_free(puVar1);
        file_heap_free(iVar2);
        uVar3 = 0;
      }
      else {
        uVar3 = Thread_MsgPbNotifyByBle(1,8,iVar2,local_34 & 0xffff);
        file_heap_free(puVar1);
        file_heap_free(iVar2);
      }
    }
  }
  return uVar3;
}

