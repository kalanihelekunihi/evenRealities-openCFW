
void RPC_SystemTimeSync(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_40 [4];
  undefined1 local_3c;
  undefined1 local_3b;
  undefined4 local_38;
  int local_34;
  undefined1 auStack_30 [4];
  int local_2c;
  int local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_0047ef10(auStack_30);
    uVar3 = service_time_calendar_to_epoch(auStack_30);
    FUN_00439c04(auStack_40,DAT_0044a428,0x10);
    local_3c = FUN_0045a568();
    iVar2 = FUN_0045a568();
    piVar1 = DAT_0044a40c;
    if (iVar2 == 1) {
      local_3b = 2;
    }
    else {
      local_3b = 1;
    }
    local_34 = (int)*(char *)(*DAT_0044a40c + 8);
    local_38 = uVar3;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0044a420,DAT_0044a41c,DAT_0044a430,0xd1,DAT_0044a42c,local_24 + 2000,
                   local_20,local_1c,local_18,local_14,local_10,
                   *(undefined4 *)(DAT_0044a410 + local_2c * 4),(int)*(char *)(*piVar1 + 8));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x12000000,DAT_0044a434,DAT_0044a434,local_24 + 2000,local_20,local_1c,
                          local_18,local_14,local_10,*(undefined4 *)(DAT_0044a410 + local_2c * 4),
                          (int)*(char *)(*piVar1 + 8));
    }
    FUN_004651e0(0x100,auStack_40,0x10,0);
    uVar3 = DAT_0044a438;
    fw_event_loop_remove_delayed(DAT_0044a438);
    fw_event_loop_push_delayed(uVar3,0,30000);
  }
  return;
}

