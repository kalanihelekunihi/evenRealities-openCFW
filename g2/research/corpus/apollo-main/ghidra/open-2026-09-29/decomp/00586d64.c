
undefined4
navigation_send_type_4_allocating
          (undefined1 param_1,undefined4 param_2,undefined4 param_3,uint param_4,undefined4 param_5)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint local_50;
  undefined4 local_4c;
  undefined4 local_48;
  uint local_44;
  undefined4 local_40;
  undefined1 auStack_3c [20];
  uint uStack_28;
  
  uStack_28 = param_4;
  puVar1 = (undefined1 *)file_heap_allocate(0x2024);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_4c = DAT_00586f04;
      local_50 = 0x1e7;
      FUN_0043d574(1,DAT_00586f10,DAT_00586f0c,DAT_005872c8);
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
        local_4c = DAT_00587050;
        local_50 = 0x1ee;
        FUN_0043d574(1,DAT_00586f10,DAT_00586f0c,DAT_005872c8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00587054,DAT_00587054);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(puVar1,0x2024,0);
      FUN_0043c0e4(iVar2,10000,0);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_40 = param_5;
        local_4c = DAT_005872cc;
        local_50 = 0x1f5;
        local_48 = param_2;
        local_44 = param_4;
        FUN_0043d574(3,DAT_00586f10,DAT_00586f0c,DAT_005872c8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_4c = param_5;
        local_50 = param_4;
        compress_log_output(0xcc00000,DAT_005872d0,DAT_005872d0,param_2);
      }
      *puVar1 = 4;
      puVar1[1] = param_1;
      *(undefined2 *)(puVar1 + 2) = 8;
      *(uint *)(puVar1 + 0x48) = param_4;
      *(undefined4 *)(puVar1 + 0x4c) = param_5;
      FUN_00439be4(puVar1 + 4,param_2,param_3);
      FUN_004905f4(auStack_3c,iVar2,10000);
      FUN_00439c04(&local_50,auStack_3c,0x14);
      iVar4 = FUN_00490c32(&local_50,DAT_005872b8,puVar1);
      if (iVar4 == 0) {
        file_heap_free(puVar1);
        file_heap_free(iVar2);
        uVar3 = 0;
      }
      else {
        uVar3 = Thread_MsgPbNotifyByBle(1,8,iVar2,local_44 & 0xffff);
        file_heap_free(puVar1);
        file_heap_free(iVar2);
      }
    }
  }
  return uVar3;
}

