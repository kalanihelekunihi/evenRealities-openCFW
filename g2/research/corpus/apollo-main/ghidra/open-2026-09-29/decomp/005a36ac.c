
undefined8 FUN_005a36ac(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  byte local_28 [4];
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  puVar5 = (uint *)(DAT_005a4104 + param_1 * 4 + 4);
  puVar4 = (uint *)(DAT_005a4104 + 100);
  local_28[0] = *(byte *)puVar4 & 0x7f;
  local_28[1] = (byte)(*puVar4 >> 7) & 0x7f;
  local_28[2] = (byte)(*puVar4 >> 0xe) & 0x7f;
  local_28[3] = (byte)(*puVar4 >> 0x15) & 0x7f;
  uVar3 = *puVar5;
  bVar1 = *(byte *)puVar5;
  bVar2 = local_28[param_1 & 3];
  if (*DAT_005a4108 << 0x1f < 0) {
    uVar6 = 0;
    while ((uVar6 < 0x3c && (-1 < *DAT_005a3780 << 1))) {
      FUN_004807a0(1);
      uVar6 = uVar6 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a3784 = param_3;
  *DAT_005a3788 = param_1;
  *DAT_005a378c = (*puVar5 & 0x1ffff) >> 7;
  *DAT_005a3790 = (*puVar5 & 0x1fffff) >> 0x11;
  *DAT_005a3794 = (uVar3 & 0xfffffff) >> 0x15;
  *DAT_005a40fc = bVar1 & 0x7f;
  *DAT_005a4100 = *DAT_005a4100 & 0xffffff80 | bVar2 & 0x7f;
  return CONCAT44(uStack_24,
                  CONCAT13(local_28[3],CONCAT12(local_28[2],CONCAT11(local_28[1],local_28[0]))));
}

