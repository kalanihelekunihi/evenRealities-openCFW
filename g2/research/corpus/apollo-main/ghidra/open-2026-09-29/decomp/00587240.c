
undefined4
navigation_send_type_1_shared
          (undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_48 [12];
  uint local_3c;
  undefined1 auStack_34 [20];
  undefined4 uStack_20;
  
  puVar1 = DAT_005872c0;
  uStack_20 = param_4;
  FUN_0043c0e4(DAT_005872c0,0x2024,0);
  uVar3 = DAT_005872c4;
  FUN_0043c0e4(DAT_005872c4,10000,0);
  *puVar1 = 1;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 3;
  puVar1[4] = param_2;
  FUN_004905f4(auStack_34,uVar3,10000);
  FUN_00439c04(auStack_48,auStack_34,0x14);
  iVar2 = FUN_00490c32(auStack_48,DAT_005872b8,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,8,uVar3,local_3c & 0xffff);
  }
  return uVar3;
}

