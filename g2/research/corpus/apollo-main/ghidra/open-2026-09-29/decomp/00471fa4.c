
undefined4 sync_info_fn_00471fa4(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_40;
  undefined4 local_3c;
  undefined1 auStack_38 [12];
  undefined2 local_2c;
  undefined1 auStack_24 [20];
  
  puVar1 = (undefined1 *)file_heap_allocate(0xc);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047220c,DAT_00472208,DAT_00472218,0x51,DAT_00472214);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047221c,DAT_0047221c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = file_heap_allocate(0x80);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0047220c,DAT_00472208,DAT_00472218,0x58,DAT_00472220);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00472224);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(puVar1,0xc,0);
      FUN_0043c0e4(iVar2,0x80,0);
      *puVar1 = 1;
      puVar1[1] = 0;
      FUN_00443504(&local_3c,&local_40);
      puVar1[2] = 1;
      *(undefined4 *)(puVar1 + 4) = local_3c;
      *(undefined4 *)(puVar1 + 8) = local_40;
      FUN_004905f4(auStack_24,iVar2,0x80);
      FUN_00439c04(auStack_38,auStack_24,0x14);
      iVar4 = FUN_00490c32(auStack_38,DAT_004721fc,puVar1);
      if (iVar4 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047220c,DAT_00472208,DAT_00472218,0x6b,DAT_00472200);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00472210,DAT_00472210);
        }
        file_heap_free(puVar1);
        file_heap_free(iVar2);
        uVar3 = 0;
      }
      else {
        uVar3 = Thread_MsgPbNotifyByBle(1,0xd,iVar2,local_2c);
        file_heap_free(puVar1);
        file_heap_free(iVar2);
      }
    }
  }
  return uVar3;
}

