
undefined4 DRV_RtcSetTime(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_30 [4];
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  local_18 = *(undefined4 *)(param_1 + 0x18);
  local_14 = *(undefined4 *)(param_1 + 0x1c);
  local_10 = *(undefined4 *)(param_1 + 0x20);
  local_c = 0;
  local_2c = FUN_004d3cf8(*(int *)(param_1 + 0xc) + 2000,*(undefined4 *)(param_1 + 0x10),
                          *(undefined4 *)(param_1 + 0x14));
  local_1c = *(undefined4 *)(param_1 + 0x14);
  local_20 = *(undefined4 *)(param_1 + 0x10);
  local_24 = *(undefined4 *)(param_1 + 0xc);
  local_28 = 1;
  iVar1 = FUN_004d3adc(auStack_30);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047ef08,DAT_0047ef04,DAT_0047ef00,0xdd,DAT_0047eefc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047ef0c);
    }
    uVar2 = 1;
  }
  return uVar2;
}

