/* ================================================================
 * entry: 0x00048a28
 * end:   0x00048abb
 * size:  148 bytes
 * name:  FUN_00048a28
 * ================================================================ */

void FUN_00048a28(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined2 uVar3;
  undefined1 local_d8 [2];
  undefined1 local_d6;
  undefined1 local_d5;
  undefined4 *local_7c;
  undefined2 *local_78;
  undefined1 auStack_60 [44];
  undefined4 local_34;
  undefined4 local_2b;
  undefined2 local_27;
  undefined4 local_24;
  undefined2 local_20 [2];
  undefined2 local_1c;
  undefined4 *local_18;
  byte local_14 [8];

  FUN_000277aa(local_d8,0xac);
  local_d8[0] = 2;
  local_d6 = 1;
  local_d5 = 6;
  local_24 = *DAT_00048abc;
  local_7c = &local_24;
  software_interrupt(0x6d);
  if (&stack0x00000000 != &SVCall) {
    FUN_0004e5bc();
  }
  puVar1 = DAT_00048ac0;
  uVar3 = 6;
  *DAT_00048ac0 = local_2b;
  *(undefined2 *)(puVar1 + 1) = local_27;
  local_14[0] = 0;
  FUN_0007ba78((int)puVar1 + 6,local_14);
  if (0xe < local_14[0]) {
    uVar3 = 0x15;
  }
  local_20[0] = 0x5245;
  local_78 = local_20;
  local_18 = puVar1;
  local_1c = uVar3;
  FUN_000489e6(auStack_60);
  local_34 = DAT_00048ac4;
  iVar2 = FUN_00051716(DAT_00048ac0 + 0x18,local_d8);
  if (iVar2 != 0) {
    FUN_0004e5bc();
  }
  FUN_00051710(DAT_00048ac0 + 0x18,1);
  return;
}



