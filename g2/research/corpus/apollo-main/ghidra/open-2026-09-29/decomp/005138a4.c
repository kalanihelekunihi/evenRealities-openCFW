
void FUN_005138a4(void)

{
  undefined1 *puVar1;
  uint uVar2;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  local_30 = DAT_00513ea8;
  uStack_2c = DAT_00513eac;
  uStack_28 = DAT_00513eb0;
  uStack_24 = DAT_00513eb4;
  uStack_20 = DAT_00513eb8;
  uStack_1c = DAT_00513ebc;
  FUN_00522920(&local_30,1,0x18);
  FUN_00522920(&local_30,1,0x19);
  FUN_00522920(&local_30,1,0x1a);
  FUN_00522920(&local_30,1,0x1b);
  FUN_00522920(&local_30,1,0x1c);
  FUN_00522920(&local_30,1,0x1d);
  FUN_00522920(&local_30,1,0x1e);
  FUN_00522920(&uStack_28,1,0x1f);
  uVar2 = FUN_00522602();
  puVar1 = DAT_00513e70;
  uVar2 = uVar2 >> 0x1c & 1;
  *DAT_00513e70 = (char)uVar2;
  if (uVar2 != 0) {
    *(undefined4 *)(puVar1 + 4) = 0;
    FUN_00522956(1);
  }
  return;
}

