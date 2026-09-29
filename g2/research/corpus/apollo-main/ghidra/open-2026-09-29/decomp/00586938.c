
undefined4 navigation_send_type_0_shared(undefined1 param_1)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_40 [12];
  uint local_34;
  undefined1 auStack_2c [20];
  
  puVar1 = DAT_005872c0;
  FUN_0043c0e4(DAT_005872c0,0x2024,0);
  uVar3 = DAT_005872c4;
  FUN_0043c0e4(DAT_005872c4,10000,0);
  *puVar1 = 0;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 3;
  puVar1[4] = 0;
  FUN_004905f4(auStack_2c,uVar3,10000);
  FUN_00439c04(auStack_40,auStack_2c,0x14);
  iVar2 = FUN_00490c32(auStack_40,DAT_005872b8,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,8,uVar3,local_34 & 0xffff);
  }
  return uVar3;
}

