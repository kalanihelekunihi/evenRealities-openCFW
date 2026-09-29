
undefined4 FUN_00471bca(int param_1,short *param_2)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint *puVar12;
  
  iVar6 = DAT_00471ed0;
  iVar11 = *(int *)(param_2 + 6);
  uVar7 = *(uint *)(param_2 + 8);
  uVar8 = *(uint *)(param_2 + 10);
  if ((param_1 == 0xe) || (param_1 == 0xf)) {
    return 3;
  }
  cVar1 = (char)param_2[1];
  if (cVar1 == '\x01') {
    if ((uVar8 != 0xffffffff) && (uVar7 <= uVar8)) {
      return 7;
    }
  }
  else if ((cVar1 != '\x02') && (cVar1 != '\x04')) {
    if ((cVar1 != '\f') && (cVar1 != '\r')) {
      return 7;
    }
    if (0x3f < *(uint *)(param_2 + 6)) {
      return 7;
    }
  }
  uVar10 = DAT_00471ecc & (int)*param_2 << 8;
  bVar2 = *(byte *)(param_2 + 1);
  bVar3 = *(byte *)(param_2 + 2);
  bVar4 = *(byte *)((int)param_2 + 3);
  bVar5 = *(byte *)((int)param_2 + 5);
  uVar9 = DAT_00471ecc & (int)param_2[3] << 8;
  puVar12 = (uint *)(DAT_00471ed0 + param_1 * 0x20 + 0x200);
  *puVar12 = *puVar12 & 0xfffffffe;
  *(uint *)(iVar6 + param_1 * 0x20 + 0x200) =
       uVar10 | (bVar2 & 0xf) << 4 | (uint)bVar3 << 3 | (uint)bVar4 << 2 | (bVar5 & 3) << 0x11 |
       iVar11 << 0x18;
  *(uint *)(iVar6 + param_1 * 0x20 + 0x210) = uVar9;
  *(uint *)(iVar6 + param_1 * 0x20 + 0x208) = uVar7;
  *(uint *)(iVar6 + param_1 * 0x20 + 0x20c) = uVar8;
  puVar12 = (uint *)(iVar6 + param_1 * 0x20 + 0x200);
  *puVar12 = *puVar12 | 2;
  return 0;
}

