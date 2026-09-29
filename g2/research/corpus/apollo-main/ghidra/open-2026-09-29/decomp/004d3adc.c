
undefined8 FUN_004d3adc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar3 = FUN_004d3a58(param_1);
  puVar1 = DAT_004d3cd4;
  if (iVar3 != 0) {
    *DAT_004d3cd4 = *DAT_004d3cd4 | 1;
    uVar4 = FUN_004d3a38(*(uint *)(param_1 + 0x18) & 0xff);
    uVar5 = FUN_004d3a38(*(uint *)(param_1 + 0x1c) & 0xff);
    bVar2 = FUN_004d3a38(*(uint *)(param_1 + 0x20) & 0xff);
    uVar6 = FUN_004d3a38(*(uint *)(param_1 + 0x24) & 0xff);
    *DAT_004d3cd8 = (uVar4 & 0x3f) << 0x18 | (uVar5 & 0x7f) << 0x10 | (bVar2 & 0x7f) << 8 | uVar6;
    uVar4 = FUN_004d3a38(*(uint *)(param_1 + 0xc) & 0xff);
    uVar5 = FUN_004d3a38(*(uint *)(param_1 + 0x10) & 0xff);
    bVar2 = FUN_004d3a38(*(uint *)(param_1 + 0x14) & 0xff);
    *DAT_004d3cdc =
         (uVar5 & 0x1f) << 8 |
         (*(uint *)(param_1 + 8) & 1) << 0x1c | (*(uint *)(param_1 + 4) & 7) << 0x18 |
         (uVar4 & 0xff) << 0x10 | bVar2 & 0x3f;
    *puVar1 = *puVar1 & 0xfffffffe;
  }
  return CONCAT44(param_4,(uint)(iVar3 == 0));
}

