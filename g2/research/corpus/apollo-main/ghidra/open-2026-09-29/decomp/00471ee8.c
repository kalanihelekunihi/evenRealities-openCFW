
uint sync_info_fn_00471ee8
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 local_48;
  undefined4 local_44;
  undefined1 auStack_40 [12];
  uint local_34;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  puVar1 = DAT_004721f4;
  uStack_18 = param_4;
  FUN_0043c0e4(DAT_004721f4,0xc,0);
  uVar2 = DAT_004721f8;
  FUN_0043c0e4(DAT_004721f8,0x80,0);
  *puVar1 = 0;
  puVar1[1] = param_1;
  FUN_00443504(&local_44,&local_48);
  puVar1[2] = 1;
  *(undefined4 *)(puVar1 + 4) = local_44;
  *(undefined4 *)(puVar1 + 8) = local_48;
  FUN_004905f4(auStack_2c,uVar2,0x80);
  FUN_00439c04(auStack_40,auStack_2c,0x14);
  iVar3 = FUN_00490c32(auStack_40,DAT_004721fc,puVar1);
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047220c,DAT_00472208,DAT_00472204,0x3c,DAT_00472200);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00472210,DAT_00472210);
    }
    uVar4 = 0;
  }
  else {
    uVar4 = Thread_MsgPbTxByBle(1,0xd,uVar2,local_34 & 0xffff);
    if (uVar4 == 0) {
      for (uVar4 = 0; uVar4 < local_34; uVar4 = uVar4 + 1) {
      }
    }
  }
  return uVar4;
}

