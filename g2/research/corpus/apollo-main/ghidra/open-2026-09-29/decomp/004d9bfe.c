
undefined4 FUN_004d9bfe(undefined1 param_1,undefined1 param_2,undefined4 param_3)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_48 [12];
  uint local_3c;
  undefined1 auStack_34 [20];
  
  FUN_004d9b4a();
  puVar1 = DAT_004da6cc;
  FUN_0043c0e4(DAT_004da6cc,0x3758,0);
  uVar3 = DAT_004da6d0;
  FUN_0043c0e4(DAT_004da6d0,0x38ec,0);
  *puVar1 = 0xc;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 0xf;
  puVar1[8] = param_2;
  *(undefined4 *)(puVar1 + 4) = param_3;
  FUN_004d9ba6();
  FUN_004905f4(auStack_34,uVar3,0x38ec);
  FUN_00439c04(auStack_48,auStack_34,0x14);
  iVar2 = FUN_00490c32(auStack_48,DAT_004da7c8,puVar1);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,0xe0,uVar3,local_3c & 0xffff);
  }
  return uVar3;
}

