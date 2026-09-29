
undefined4
FUN_004da4a4(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8,
            undefined4 param_9)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_58 [12];
  uint local_4c;
  undefined1 auStack_44 [24];
  undefined4 local_2c;
  undefined4 local_28;
  
  local_2c = param_1;
  local_28 = param_4;
  FUN_004d9b4a();
  puVar1 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar1 = 4;
  puVar1[1] = (undefined1)local_2c;
  *(undefined2 *)(puVar1 + 2) = 6;
  *(undefined4 *)(puVar1 + 4) = param_3;
  FUN_0044b5a0(puVar1 + 8,local_28,0x10);
  *(undefined4 *)(puVar1 + 0x18) = param_5;
  *(undefined4 *)(puVar1 + 0x1c) = param_6;
  *(undefined4 *)(puVar1 + 0x20) = param_7;
  *(undefined4 *)(puVar1 + 0x24) = param_8;
  *(undefined4 *)(puVar1 + 0x28) = param_9;
  puVar1[0x2c] = param_2;
  FUN_004d9ba6();
  FUN_004905f4(auStack_44,DAT_004da6d0,0x38ec);
  FUN_00439c04(auStack_58,auStack_44,0x14);
  iVar2 = FUN_00490c32(auStack_58,DAT_004da7c8,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,0xe0,DAT_004da6d0,local_4c & 0xffff);
  }
  return uVar3;
}

