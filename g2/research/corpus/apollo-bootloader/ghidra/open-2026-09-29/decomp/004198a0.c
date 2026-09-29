
void FUN_004198a0(void)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = DAT_00419964;
  iVar3 = 0x14000;
  puVar2 = DAT_00419974;
  if (((uint)DAT_00419974 & 7) != 0) {
    puVar2 = (uint *)((int)DAT_00419974 + 7U & 0xfffffff8);
    iVar3 = (int)DAT_00419974 + (0x14000 - (int)puVar2);
  }
  *DAT_00419964 = (uint)puVar2;
  puVar1[1] = 0;
  puVar1 = DAT_00419958;
  uVar4 = (int)puVar2 + (iVar3 - *DAT_0041995c) & 0xfffffff8;
  *DAT_00419958 = uVar4;
  *(undefined4 *)(*puVar1 + 4) = 0;
  *(undefined4 *)*puVar1 = 0;
  puVar2[1] = uVar4 - (int)puVar2;
  *puVar2 = *puVar1;
  *DAT_00419968 = puVar2[1];
  *DAT_00419960 = puVar2[1];
  return;
}

