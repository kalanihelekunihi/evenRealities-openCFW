
undefined4 FUN_00471224(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_40 [12];
  undefined2 local_34;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,DAT_00471af0,0x6c,DAT_00471aec);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00471af4,DAT_00471af4);
  }
  puVar1 = DAT_00471af8;
  FUN_0043c0e4(DAT_00471af8,8,0);
  uVar3 = DAT_00471afc;
  FUN_0043c0e4(DAT_00471afc,0xd,0);
  *puVar1 = 0;
  puVar1[1] = param_1;
  FUN_004905f4(auStack_2c,uVar3,0xd);
  FUN_00439c04(auStack_40,auStack_2c,0x14);
  iVar2 = FUN_00490c32(auStack_40,DAT_00471b00,puVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00471ae0,DAT_00471adc,DAT_00471af0,0x75,DAT_00471b04);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00471b08,DAT_00471b08);
    }
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,0x20,uVar3,local_34,0);
  }
  return uVar3;
}

