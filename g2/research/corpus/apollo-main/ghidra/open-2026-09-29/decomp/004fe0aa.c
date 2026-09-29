
undefined4 FUN_004fe0aa(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_34 [12];
  uint local_28;
  int local_24;
  undefined1 auStack_20 [20];
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004fe300,DAT_004fe2fc,DAT_004fec0c,0x1b4,DAT_004fec08);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004fec10,DAT_004fec10);
  }
  uVar3 = DAT_004fec80;
  FUN_0043c0e4(DAT_004fec80,0x100,0);
  puVar1 = DAT_004fec84;
  FUN_004fdd6e(DAT_004fec84);
  *puVar1 = 0xb;
  *(undefined4 *)(puVar1 + 4) = 1;
  *(undefined2 *)(puVar1 + 8) = 0xd;
  *(undefined4 *)(puVar1 + 0x10) = 1;
  FUN_004905f4(auStack_20,uVar3,0x100);
  FUN_00439c04(auStack_34,auStack_20,0x14);
  iVar2 = FUN_00490c32(auStack_34,DAT_004fec88,puVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar2 = DAT_004fec8c;
      if (local_24 != 0) {
        iVar2 = local_24;
      }
      FUN_0043d574(1,DAT_004fe300,DAT_004fe2fc,DAT_004fec0c,0x1be,DAT_004fec90,iVar2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      iVar2 = DAT_004fec8c;
      if (local_24 != 0) {
        iVar2 = local_24;
      }
      compress_log_output(0x4400000,PTR_s__dashboard_data_process_SendNews_004fedc0,
                          PTR_s__dashboard_data_process_SendNews_004fedc0,iVar2);
    }
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbNotifyByBle(1,1,uVar3,local_28 & 0xffff);
  }
  return uVar3;
}

