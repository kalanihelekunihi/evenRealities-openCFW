
void FUN_00513924(uint param_1,uint param_2,uint param_3,uint param_4)

{
  byte bVar1;
  byte bVar2;
  bool bVar3;
  bool bVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  byte bVar19;
  int iVar20;
  byte local_88;
  undefined1 local_86;
  undefined4 local_84;
  uint local_7c;
  uint local_74;
  uint local_68 [17];
  
  local_7c = param_4;
  if (DAT_00513e70[1] != '\0') {
    FUN_00522a16(0x20202020);
    param_3 = 0xffffffff;
    local_7c = 0xffffffff;
    param_1 = 0x101;
    FUN_004b1588(0);
  }
  uVar5 = param_1 >> 0x17;
  uVar8 = param_1 >> 0x16;
  uVar12 = -((int)param_1 >> 0x1f);
  uVar10 = param_1 >> 0x15;
  uVar6 = param_1 & 0xfff00000;
  local_88 = (byte)(param_1 >> 0x14) & 1;
  uVar17 = param_1 & 0xf;
  uVar14 = (param_1 & 0xfff) >> 8;
  uVar15 = param_1 >> 0x19 & 1;
  if (3 < param_2) {
    param_2 = 0;
  }
  if (3 < param_3) {
    param_3 = 0xffffffff;
  }
  local_84._0_3_ = (uint3)(byte)local_7c << 0x10;
  if (3 < local_7c) {
    local_84._0_3_ = 0x20000;
    local_7c = param_2;
  }
  uVar7 = 0;
  if (*DAT_00513e70 != '\0') {
    uVar7 = 0;
    if (uVar12 != 0) {
      uVar7 = 0x80000000;
      uVar12 = 0;
      param_1 = param_1 & 0x7fffffff;
    }
    if (uVar15 != 0) {
      uVar7 = uVar7 | 0x2000000;
      uVar15 = 0;
      param_1 = param_1 & 0xfdffffff;
    }
    if (((int)(param_1 << 7) < 0) || (local_7c != param_2)) {
      FUN_00522956(uVar7 | 1);
      uVar7 = 0;
      local_88 = 0;
    }
    else {
      uVar9 = uVar17 | uVar14 << 8;
      uVar14 = 0;
      uVar17 = 1;
      uVar7 = FUN_00522956(uVar7 | uVar9);
      param_1 = param_1 & 0xfff00000 | 1;
    }
  }
  uVar12 = uVar15 | uVar12;
  if (param_1 == 1) {
    uVar7 = (uint)*(byte *)(*DAT_00513e74 + 10);
  }
  if ((param_1 == 1 && uVar7 == 0) && (param_2 == 0)) {
    if ((int)param_3 < 0) {
      FUN_005226d6(1);
      uVar5 = DAT_00513e78 | *(int *)(DAT_00513e70 + 4) << 0x10;
    }
    else {
      FUN_005226d6();
      uVar5 = *(uint *)(&LAB_00513ec0 + param_3 * 4) | *(int *)(DAT_00513e70 + 4) << 0x10 |
              DAT_00513e7c;
    }
    goto LAB_00513dfe;
  }
  bVar2 = (byte)(param_1 >> 0x18);
  bVar19 = bVar2 >> 6 & 1;
  bVar1 = bVar2 >> 3 & 1;
  local_86 = 1;
  iVar13 = 0;
  local_84 = CONCAT31(CONCAT21((short)(CONCAT13((char)uVar8,(int3)local_84) >> 0x10),bVar2 >> 5),
                      bVar2 >> 2) & 0x1ff0101;
  uVar8 = param_1 >> 0x1c & 1;
  if ((uVar17 < 6) && (uVar12 == 0 && uVar14 == 0)) {
    bVar4 = false;
    uVar7 = 0;
  }
  else {
    bVar4 = true;
    uVar7 = 3;
  }
  uVar9 = (uint)bVar19;
  if (uVar8 == 0) {
    local_74 = 3;
  }
  else {
    local_74 = 1;
  }
  if (uVar15 == 0) {
    uVar15 = uVar12 << 0x15;
  }
  else {
    uVar15 = 0x100000;
  }
  if (local_88 == 0) {
    if (local_84._1_1_ == '\0') {
      if ((char)local_84 == '\0') {
        iVar18 = 0x1d;
      }
      else {
        iVar18 = 4;
      }
    }
    else {
      iVar18 = 0x11;
    }
  }
  else {
    iVar18 = 0x17;
  }
  if (uVar8 == 0 && bVar1 == 0) {
    iVar20 = 0xe;
  }
  else {
    iVar20 = 0xc;
  }
  local_68[0] = 0;
  uVar16 = 0;
  if (*(char *)(*DAT_00513e74 + 10) == '\0') {
    if ((int)param_3 < 0) {
      if (bVar4) {
        bVar4 = false;
        uVar7 = 0;
        uVar16 = *(uint *)(&LAB_00513ec0 + local_7c * 4) | 0xb000;
      }
    }
    else {
      local_86 = 0;
      uVar16 = *(uint *)(&LAB_00513ec0 + param_3 * 4) | 0x8000;
    }
    if ((uVar5 & 1) == 0) {
      bVar3 = false;
      if (local_84._3_1_ != '\0') {
        uVar16 = 0xdc00;
        goto LAB_00513bb2;
      }
    }
    else {
      uVar16 = 0xcc00;
LAB_00513bb2:
      bVar3 = true;
    }
    if ((uVar10 & 1) == 0 || param_3 == 0xffffffff) {
      if (bVar3) {
        local_68[0] = DAT_00513e88 | param_3 << 7;
        local_68[1] = 0x2000;
        iVar13 = 1;
      }
    }
    else {
      local_68[0] = DAT_00513e8c | param_3 << 7;
      local_68[1] = 0x2000;
      local_68[2] = (int)local_84._2_1_ << 7 | 0x100b;
      local_68[3] = 0;
      iVar13 = 2;
    }
    if ((uVar5 & 1) != 0 || local_84._3_1_ != '\0') {
      local_68[iVar13 * 2] = 0xc0000;
      local_68[iVar13 * 2 + 1] = DAT_00513e90;
      iVar13 = iVar13 + 1;
    }
  }
  else {
    local_68[0] = DAT_00513e80;
    iVar13 = 1;
    uVar16 = 0xfc00;
    local_68[1] = DAT_00513e84;
    if (-1 < (int)param_3) {
      local_68[2] = DAT_00513e88 | param_3 << 7;
      local_68[3] = 0x2000;
      local_86 = 0;
      iVar13 = 2;
    }
  }
  bVar3 = true;
  if ((((uVar14 < 2) && ((int)-(uint)(uVar6 == 0) < 0)) && ((int)param_3 < 0)) &&
     (local_7c == param_2)) {
    if (uVar14 == 0) {
      uVar5 = 0x2000;
      uVar6 = 0x800000;
    }
    else {
      uVar5 = 0x800;
      uVar6 = 0x200000;
    }
    local_68[iVar13 * 2 + 1] =
         uVar5 | *(int *)(DAT_00513e94 + uVar17 * 4) << 0xe |
         *(int *)(DAT_00513e94 + 0x30 + uVar17 * 4) << 5 | uVar6 | 0x8a000006;
    uVar5 = DAT_00513e98 | param_2 << 7;
LAB_00513dca:
    local_68[iVar13 * 2] = uVar5;
    iVar13 = iVar13 + 1;
  }
  else {
    if ((uVar17 < 6) &&
       ((((local_88 == 0 && local_84._1_1_ == '\0') && (char)local_84 == '\0') && bVar1 == 0) &&
        uVar8 == 0)) {
      local_84 = uVar7 | DAT_00513e9c;
      uVar5 = uVar9 << 0x14;
LAB_00513d48:
      uVar10 = 0;
      uVar6 = 0x1000;
      uVar8 = 0x400000;
      if (uVar14 == 0) {
        uVar9 = uVar12;
      }
      if (uVar14 != 0 || uVar9 != 0) {
        uVar12 = local_7c;
        if (bVar4 || bVar19 != 0) goto LAB_00513d68;
        if (uVar17 == 0) {
          uVar6 = 0x2000;
          uVar8 = 0x800000;
        }
        else {
          if (uVar17 != 1) goto LAB_00513d68;
          uVar6 = 0;
          uVar8 = 0;
        }
      }
      else {
        uVar10 = 0x80000000;
        local_84 = DAT_00513e98;
        uVar12 = param_2;
LAB_00513d68:
        local_68[iVar13 * 2 + 1] =
             DAT_00513ea0 |
             uVar10 | *(int *)(DAT_00513e94 + uVar17 * 4) << 0xe |
             *(int *)(DAT_00513e94 + 0x30 + uVar17 * 4) << 5;
        local_68[iVar13 * 2] = uVar5 | local_84 | (int)(char)uVar12 << 7;
        iVar13 = iVar13 + 1;
        if (uVar10 != 0) goto LAB_00513dd0;
      }
      local_68[iVar13 * 2 + 1] =
           uVar8 | uVar6 | *(int *)(DAT_00513e94 + uVar14 * 4) << 0xe |
                   *(int *)(DAT_00513e94 + 0x30 + uVar14 * 4) << 5 | DAT_00513ea4;
      uVar5 = uVar15 | param_2 << 7 | 0x4e0002;
      goto LAB_00513dca;
    }
    if (local_88 == 0) {
      iVar11 = 4;
    }
    else {
      iVar11 = 7;
    }
    uVar6 = uVar14 | uVar7;
    uVar5 = uVar6;
    if (uVar6 == 0) {
      uVar5 = uVar12;
    }
    if (uVar6 != 0 || uVar5 != 0) {
LAB_00513cfa:
      if ((iVar18 != 0x1d || iVar20 != 0xe) || (uVar9 != 0 || uVar7 != 0)) {
        local_68[iVar13 * 2 + 1] = local_74 | iVar20 << 5 | iVar18 << 0xe | iVar11 << 0xb | 4;
        local_68[iVar13 * 2] = uVar7 | local_7c << 7 | uVar9 << 0x14 | DAT_00513e9c;
        goto LAB_00513d38;
      }
    }
    else {
      if (uVar17 == 1) {
        uVar5 = (uint)bVar19;
      }
      if (uVar17 != 1 || uVar5 != 0) goto LAB_00513cfa;
      bVar3 = false;
      local_68[iVar13 * 2 + 1] = local_74 | iVar20 << 5 | iVar18 << 0xe | iVar11 << 0xb | 0x80000004
      ;
      uVar9 = uVar9 << 0x14 | param_2 << 7 | DAT_00513e98;
      local_68[iVar13 * 2] = uVar9;
LAB_00513d38:
      iVar13 = iVar13 + 1;
    }
    uVar5 = 0;
    bVar4 = false;
    local_84 = DAT_00513e9c;
    bVar19 = 0;
    if (bVar3) goto LAB_00513d48;
  }
LAB_00513dd0:
  FUN_005226d6(local_86);
  FUN_00522920(local_68,iVar13,0);
  uVar5 = uVar16 | (0x20U - iVar13 |
                   *(uint *)(DAT_00513e70 + 4) | *(uint *)(&LAB_00513ec0 + local_7c * 4)) << 0x10 |
          0x10000000;
LAB_00513dfe:
  FUN_0052294c(uVar5);
  return;
}

