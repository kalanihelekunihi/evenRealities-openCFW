
undefined4
af_face_globals_compute_style_coverage
          (int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  uint local_38;
  uint local_34;
  uint local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  iVar3 = *param_1;
  local_2c = *(undefined4 *)(iVar3 + 0x5c);
  iVar4 = param_1[2];
  local_30 = 0xffffffff;
  for (uVar1 = 0; uVar1 < (uint)param_1[1]; uVar1 = uVar1 + 1) {
    *(undefined2 *)(iVar4 + uVar1 * 2) = 0x3fff;
  }
  uStack_28 = param_4;
  iVar2 = FT_Select_Charmap(iVar3,DAT_005a7fa4);
  if (iVar2 == 0) {
    for (uVar1 = 0; *(int *)(DAT_005a7fa8 + uVar1 * 4) != 0; uVar1 = uVar1 + 1) {
      iVar2 = *(int *)(DAT_005a7fa8 + uVar1 * 4);
      iVar5 = *(int *)(DAT_005a7fac + (uint)*(byte *)(iVar2 + 2) * 4);
      if ((*(int *)(iVar5 + 4) != 0) && (*(char *)(iVar2 + 4) == '\n')) {
        if ((uint)*(byte *)(iVar2 + 2) == *(uint *)(param_1[0x5e] + 0x10)) {
          local_30 = uVar1;
        }
        for (puVar6 = *(uint **)(iVar5 + 4); *puVar6 != 0; puVar6 = puVar6 + 2) {
          uVar7 = *puVar6;
          local_34 = FT_Get_Char_Index(iVar3,uVar7);
          if (((local_34 != 0) && (local_34 < (uint)param_1[1])) &&
             ((*(ushort *)(iVar4 + local_34 * 2) & 0x3fff) == 0x3fff)) {
            *(short *)(iVar4 + local_34 * 2) = (short)uVar1;
          }
          while ((uVar7 = FT_Get_First_Char(iVar3,uVar7,&local_34), local_34 != 0 &&
                 (uVar7 <= puVar6[1]))) {
            if ((local_34 < (uint)param_1[1]) &&
               ((*(ushort *)(iVar4 + local_34 * 2) & 0x3fff) == 0x3fff)) {
              *(short *)(iVar4 + local_34 * 2) = (short)uVar1;
            }
          }
        }
        for (puVar6 = *(uint **)(iVar5 + 8); *puVar6 != 0; puVar6 = puVar6 + 2) {
          uVar7 = *puVar6;
          local_38 = FT_Get_Char_Index(iVar3,uVar7);
          if (((local_38 != 0) && (local_38 < (uint)param_1[1])) &&
             ((*(ushort *)(iVar4 + local_38 * 2) & 0x3fff) == (uVar1 & 0xffff))) {
            *(ushort *)(iVar4 + local_38 * 2) = *(ushort *)(iVar4 + local_38 * 2) | 0x4000;
          }
          while ((uVar7 = FT_Get_First_Char(iVar3,uVar7,&local_38), local_38 != 0 &&
                 (uVar7 <= puVar6[1]))) {
            if ((local_38 < (uint)param_1[1]) &&
               ((*(ushort *)(iVar4 + local_38 * 2) & 0x3fff) == (uVar1 & 0xffff))) {
              *(ushort *)(iVar4 + local_38 * 2) = *(ushort *)(iVar4 + local_38 * 2) | 0x4000;
            }
          }
        }
      }
    }
    for (iVar2 = 0; *(int *)(DAT_005a7fa8 + iVar2 * 4) != 0; iVar2 = iVar2 + 1) {
    }
    for (uVar1 = 0x30; uVar1 < 0x3a; uVar1 = uVar1 + 1) {
      uVar7 = FT_Get_Char_Index(iVar3,uVar1);
      if ((uVar7 != 0) && (uVar7 < (uint)param_1[1])) {
        *(ushort *)(iVar4 + uVar7 * 2) = *(ushort *)(iVar4 + uVar7 * 2) | 0x8000;
      }
    }
  }
  if (*(int *)(param_1[0x5e] + 0xc) != 0x3fff) {
    for (iVar2 = 0; iVar2 < param_1[1]; iVar2 = iVar2 + 1) {
      if ((*(ushort *)(iVar4 + iVar2 * 2) & 0x3fff) == 0x3fff) {
        *(ushort *)(iVar4 + iVar2 * 2) = *(ushort *)(iVar4 + iVar2 * 2) & 0xc000;
        *(ushort *)(iVar4 + iVar2 * 2) =
             *(ushort *)(iVar4 + iVar2 * 2) | (ushort)*(undefined4 *)(param_1[0x5e] + 0xc);
      }
    }
  }
  FT_Set_Charmap(iVar3,local_2c);
  return 0;
}

