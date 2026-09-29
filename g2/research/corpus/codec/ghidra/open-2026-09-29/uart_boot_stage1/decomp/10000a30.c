
void gx8002_uart_stage1_railb(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  byte *pbVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iStack_24;
  int iStack_20;
  uint *puStack_1c;
  uint *puStack_18;
  int *piStack_14;
  int *piStack_10;
  
  iVar1 = gx8002_uart_stage1_pmu_fill_desc(param_1,&iStack_24);
  if (iVar1 == 0) {
    pbVar4 = *(byte **)(iStack_24 + 8);
    if ((pbVar4 != (byte *)0x0) && (uVar2 = (uint)*pbVar4, uVar2 != 0)) {
      uVar8 = (uint)pbVar4[1];
      uVar7 = (uint)*(ushort *)(pbVar4 + 2);
      uVar5 = *(uint *)(iStack_20 + uVar2) >> (uVar8 & 0x3f) & uVar7;
      if (uVar5 != 0) {
        uVar5 = uVar5 + 1;
      }
      if ((param_2 & 0x7fff) != uVar5) {
        if (uVar7 == 0) {
          uVar5 = 0;
        }
        else {
          uVar5 = 0;
          do {
            uVar5 = uVar5 + 1;
          } while (*(ushort *)(pbVar4 + 2) >> (uVar5 & 0x3f) != 0);
        }
        uVar10 = (uint)*(char *)(iStack_24 + 4);
        uVar11 = (uint)*(char *)(iStack_24 + 6);
        if ((int)uVar10 < 0) {
          uVar9 = 0;
        }
        else {
          uVar9 = *puStack_18 >> (uVar10 & 0x3f) & 1;
          if (uVar9 != 0) {
            *piStack_10 = 1 << (uVar10 & 0x3f);
          }
        }
        uVar6 = *puStack_1c >> (uVar11 & 0x3f) & 1;
        if ((uVar6 != 0) && ((param_1 == 6 || (9 < param_1)))) {
          *puStack_1c = (-2 << (uVar11 & 0x3f) | 0xfffffffeU >> 0x20 - (uVar11 & 0x3f)) &
                        *puStack_1c;
        }
        puVar3 = (uint *)(uVar2 + iStack_20);
        uVar2 = 1 << (uVar8 + uVar5 + 1 & 0x3f);
        *puVar3 = *puVar3 & ~uVar2;
        *puVar3 = uVar2 | *puVar3;
        *puVar3 = *puVar3 & ~(uVar7 << (uVar8 & 0x3f));
        uVar2 = 0;
        if ((param_2 & 0xffff) != 0) {
          uVar2 = (param_2 & 0x7fff) - 1 << (uVar8 & 0x3f);
        }
        *puVar3 = uVar2 | *puVar3;
        uVar2 = 1 << (uVar8 + uVar5 & 0x3f);
        *puVar3 = *puVar3 & ~uVar2;
        *puVar3 = uVar2 | *puVar3;
        if ((uVar6 != 0) && ((param_1 == 6 || (9 < param_1)))) {
          uVar2 = 1 << (uVar11 & 0x3f);
          *puStack_1c = uVar2 | *puStack_1c & ~uVar2;
        }
        if (uVar9 != 0) {
          *piStack_14 = 1 << (uVar10 & 0x3f);
        }
      }
    }
  }
  return;
}

