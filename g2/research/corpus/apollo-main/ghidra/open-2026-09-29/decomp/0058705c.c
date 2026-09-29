
undefined4
navigation_send_type_15_allocating
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_48;
  undefined4 local_44;
  uint local_3c;
  undefined1 auStack_34 [20];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  puVar1 = (undefined1 *)file_heap_allocate(0x2024);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_44 = DAT_005872d4;
      local_48 = 0x248;
      FUN_0043d574(1,DAT_005872e0,DAT_005872dc,DAT_005872e4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005872e8,DAT_005872e8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = file_heap_allocate(10000);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_44 = DAT_005872ec;
        local_48 = 0x24f;
        FUN_0043d574(1,DAT_005872e0,DAT_005872dc,DAT_005872e4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005872f0);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(puVar1,0x2024,0);
      FUN_0043c0e4(iVar2,10000,0);
      *puVar1 = 0xf;
      puVar1[1] = 0;
      *(undefined2 *)(puVar1 + 2) = 10;
      *(undefined4 *)(puVar1 + 4) = param_1;
      FUN_004905f4(auStack_34,iVar2,10000);
      FUN_00439c04(&local_48,auStack_34,0x14);
      iVar4 = FUN_00490c32(&local_48,DAT_005872b8,puVar1);
      if (iVar4 == 0) {
        file_heap_free(puVar1);
        file_heap_free(iVar2);
        uVar3 = 0;
      }
      else {
        uVar3 = Thread_MsgPbNotifyByBle(1,8,iVar2,local_3c & 0xffff);
        file_heap_free(puVar1);
        file_heap_free(iVar2);
      }
    }
  }
  return uVar3;
}

