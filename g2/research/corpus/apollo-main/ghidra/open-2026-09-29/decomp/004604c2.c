
undefined4 FUN_004604c2(undefined1 param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_48 [12];
  undefined2 local_3c;
  undefined1 auStack_34 [20];
  undefined4 uStack_20;
  
  puVar1 = DAT_00460e14;
  uStack_20 = param_4;
  FUN_0043c0e4(DAT_00460e14,0x37c,0);
  uVar3 = DAT_00460e18;
  FUN_0043c0e4(DAT_00460e18,0x432,0);
  *puVar1 = 1;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 4;
  *(uint *)(puVar1 + 4) = (uint)param_2;
  FUN_004905f4(auStack_34,uVar3,0x432);
  FUN_00439c04(auStack_48,auStack_34,0x14);
  iVar2 = FUN_00490c32(auStack_48,DAT_00460e1c,puVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0046062c,DAT_00460628,DAT_00460fac,0x147,DAT_00460e20);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00461030,DAT_00461030);
    }
    uVar3 = 0;
  }
  else {
    uVar3 = Thread_MsgPbTxByBle(1,3,uVar3,local_3c);
  }
  return uVar3;
}

