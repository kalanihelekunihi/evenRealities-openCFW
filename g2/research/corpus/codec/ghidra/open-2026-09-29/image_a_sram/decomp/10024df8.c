
void gx8002_clock_module_divider_set(uint param_1,uint param_2)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iStack_44;
  int iStack_40;
  uint *puStack_3c;
  uint *puStack_38;
  int *piStack_34;
  int *piStack_30;
  
  iVar2 = __module_get_info(param_1,&iStack_44);
  if (iVar2 == 0) {
    pbVar8 = *(byte **)(iStack_44 + 8);
    if ((pbVar8 != (byte *)0x0) && (*pbVar8 != 0)) {
      uVar3 = __module_get_div_isra_1(iStack_44,iStack_40);
      if ((param_2 & 0x7fff) != uVar3) {
        uVar11 = (uint)pbVar8[1];
        uVar1 = *(ushort *)(pbVar8 + 2);
        for (uVar3 = 0; uVar1 >> (uVar3 & 0x3f) != 0; uVar3 = uVar3 + 1) {
        }
        uVar10 = (uint)*(char *)(iStack_44 + 4);
        uVar9 = (uint)*(char *)(iStack_44 + 6);
        uVar6 = 0;
        if ((-1 < (int)uVar10) && (uVar6 = *puStack_38 >> (uVar10 & 0x3f) & 1, uVar6 != 0)) {
          *piStack_30 = 1 << (uVar10 & 0x3f);
        }
        uVar7 = *puStack_3c >> (uVar9 & 0x3f) & 1;
        if ((uVar7 != 0) && ((param_1 == 6 || (9 < param_1)))) {
          __reg_set_val(puStack_3c,uVar9,0,1);
        }
        puVar5 = (uint *)(iStack_40 + (uint)*pbVar8);
        uVar4 = 1 << (uVar3 + uVar11 + 1 & 0x3f);
        *puVar5 = *puVar5 & ~uVar4;
        *puVar5 = uVar4 | *puVar5;
        *puVar5 = *puVar5 & ~((uint)uVar1 << (uVar11 & 0x3f));
        iVar2 = 0;
        if ((param_2 & 0xffff) != 0) {
          iVar2 = (param_2 & 0x7fff) - 1;
        }
        *puVar5 = iVar2 << (uVar11 & 0x3f) | *puVar5;
        uVar3 = 1 << (uVar3 + uVar11 & 0x3f);
        *puVar5 = *puVar5 & ~uVar3;
        *puVar5 = uVar3 | *puVar5;
        if ((uVar7 != 0) && ((param_1 == 6 || (9 < param_1)))) {
          __reg_set_val(puStack_3c,uVar9,1);
        }
        if (uVar6 != 0) {
          *piStack_34 = 1 << (uVar10 & 0x3f);
        }
      }
    }
  }
  return;
}

