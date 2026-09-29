
undefined4 FUN_004da60c(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  uint local_3c;
  undefined1 auStack_34 [20];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_44 = DAT_004da80c;
    local_48 = 0x1cb;
    local_40 = param_2;
    FUN_0043d574(4,DAT_004da818,DAT_004da814,DAT_004da810);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004da654;
  }
  compress_log_output(0x10400000,DAT_004da81c,DAT_004da81c,param_2);
LAB_004da654:
  FUN_004d9b4a();
  puVar1 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  uVar3 = DAT_004da6d0;
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar1 = 0x14;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 0x17;
  *(undefined4 *)(puVar1 + 4) = param_2;
  FUN_004d9ba6();
  FUN_004905f4(auStack_34,uVar3,0x38ec);
  FUN_00439c04(&local_48,auStack_34,0x14);
  iVar2 = FUN_00490c32(&local_48,DAT_004da7c8,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,0xe0,uVar3,local_3c & 0xffff);
  }
  return uVar3;
}

