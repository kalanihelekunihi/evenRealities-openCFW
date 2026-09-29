
undefined4
navigation_send_type_8_shared
          (undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
          undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_50 [12];
  uint local_44;
  undefined1 auStack_3c [20];
  undefined4 uStack_28;
  
  puVar1 = DAT_005872c0;
  uStack_28 = param_4;
  FUN_0043c0e4(DAT_005872c0,0x2024,0);
  FUN_0043c0e4(DAT_005872c4,10000,0);
  *puVar1 = 8;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 6;
  puVar1[0x200e] = param_2;
  *(undefined4 *)(puVar1 + 0x2018) = param_3;
  *(undefined4 *)(puVar1 + 4) = param_4;
  *(undefined4 *)(puVar1 + 8) = param_5;
  *(undefined4 *)(puVar1 + 0x201c) = param_6;
  *(undefined4 *)(puVar1 + 0x2020) = param_7;
  FUN_004905f4(auStack_3c,DAT_005872c4,10000);
  FUN_00439c04(auStack_50,auStack_3c,0x14);
  iVar2 = FUN_00490c32(auStack_50,DAT_00587238,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,8,DAT_005872c4,local_44 & 0xffff);
  }
  return uVar3;
}

