
void FUN_00557890(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  bool bVar2;
  bool bVar3;
  int *piVar4;
  byte bVar5;
  char cVar6;
  char cVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int *piVar21;
  int *piVar22;
  bool bVar23;
  int local_26c;
  code *local_24c;
  int local_248;
  int local_244;
  int local_240;
  int local_23c;
  int local_238;
  int local_234;
  int local_230;
  int local_22c;
  undefined1 auStack_228 [16];
  undefined1 auStack_218 [28];
  undefined1 auStack_1fc [16];
  int local_1ec;
  undefined1 auStack_1e4 [16];
  undefined4 local_1d4;
  int local_1c8;
  byte local_1b5;
  int local_1b4;
  undefined1 local_19c;
  undefined1 local_18c;
  undefined1 local_178;
  undefined1 auStack_174 [28];
  undefined4 local_158;
  undefined1 auStack_108 [32];
  undefined1 local_e8;
  undefined1 local_cd;
  undefined1 local_c0;
  undefined1 local_b0;
  undefined1 auStack_98 [28];
  undefined4 local_7c;
  undefined1 local_78;
  undefined1 local_5d;
  undefined1 local_50;
  undefined1 local_40;
  undefined1 local_2c;
  undefined4 uStack_28;
  
  iVar8 = *param_1;
  uStack_28 = param_4;
  uVar9 = FUN_00451960(param_1);
  FUN_0043fc2a(iVar8,&local_248);
  uVar10 = FUN_005574c2(iVar8,0);
  uVar11 = FUN_005574cc(iVar8,0);
  FUN_00450b98(&local_248,uVar10,uVar11);
  iVar12 = FUN_00451598(&local_248);
  iVar13 = FUN_004515a4(&local_248);
  iVar19 = *(int *)(iVar8 + 0x34) - *(int *)(iVar8 + 0x30);
  if (iVar19 == 0) {
    iVar19 = 1;
  }
  bVar5 = *(byte *)(iVar8 + 0x70) >> 3 & 7;
  if (bVar5 == 1) {
    bVar2 = true;
  }
  else if (bVar5 == 2) {
    bVar2 = false;
  }
  else if (iVar12 < iVar13) {
    bVar2 = false;
  }
  else {
    bVar2 = true;
  }
  cVar6 = FUN_005577a6(iVar8);
  iVar14 = FUN_005574ea(iVar8,0);
  iVar15 = FUN_005574f4(iVar8,0);
  iVar16 = FUN_005574d6(iVar8,0);
  iVar17 = FUN_005574e0(iVar8,0);
  FUN_005574b0(iVar8 + 0x3c,&local_248);
  *(int *)(iVar8 + 0x3c) = iVar14 + *(int *)(iVar8 + 0x3c);
  *(int *)(iVar8 + 0x44) = *(int *)(iVar8 + 0x44) - iVar15;
  *(int *)(iVar8 + 0x40) = iVar16 + *(int *)(iVar8 + 0x40);
  *(int *)(iVar8 + 0x48) = *(int *)(iVar8 + 0x48) - iVar17;
  if ((bVar2) && (iVar18 = FUN_004515a4(iVar8 + 0x3c), iVar18 < 4)) {
    *(int *)(iVar8 + 0x40) = iVar13 / 2 + *(int *)(iVar8 + 0x18) + -2;
    *(int *)(iVar8 + 0x48) = *(int *)(iVar8 + 0x40) + 4;
  }
  else if ((!bVar2) && (iVar18 = FUN_00451598(iVar8 + 0x3c), iVar18 < 4)) {
    *(int *)(iVar8 + 0x3c) = iVar12 / 2 + *(int *)(iVar8 + 0x14) + -2;
    *(int *)(iVar8 + 0x44) = *(int *)(iVar8 + 0x3c) + 4;
  }
  iVar18 = FUN_00451598(iVar8 + 0x3c);
  local_26c = FUN_004515a4(iVar8 + 0x3c);
  if (bVar2) {
    iVar20 = 0x3c;
    iVar1 = 0x44;
    local_24c = DAT_0055800c;
    local_26c = iVar18;
  }
  else {
    iVar20 = 0x40;
    iVar1 = 0x48;
    local_24c = DAT_00558010;
  }
  piVar22 = (int *)(iVar8 + iVar20);
  if (*(int *)(iVar8 + 0x6c) == -1) {
    iVar18 = ((*(int *)(iVar8 + 0x38) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19;
  }
  else {
    iVar18 = ((*(int *)(iVar8 + 100) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19;
    iVar18 = iVar18 + (*(int *)(iVar8 + 0x6c) *
                      (((*(int *)(iVar8 + 0x68) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19 -
                      iVar18)) / 0x100;
  }
  if (*(int *)(iVar8 + 0x5c) == -1) {
    iVar20 = ((*(int *)(iVar8 + 0x2c) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19;
  }
  else {
    iVar20 = ((*(int *)(iVar8 + 0x54) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19;
    iVar20 = (*(int *)(iVar8 + 0x5c) *
             (((*(int *)(iVar8 + 0x58) - *(int *)(iVar8 + 0x30)) * local_26c) / iVar19 - iVar20)) /
             0x100 + iVar20;
  }
  cVar7 = FUN_00557512(iVar8,0);
  if ((bVar2) && (cVar7 == '\x01')) {
    cVar7 = '\x01';
  }
  else {
    cVar7 = '\0';
  }
  bVar23 = cVar7 == *(char *)(iVar8 + 0x4c);
  piVar21 = (int *)(iVar8 + iVar1);
  if (!bVar23) {
    iVar20 = -iVar20;
    iVar18 = -iVar18;
    piVar21 = piVar22;
    piVar22 = (int *)(iVar8 + iVar1);
  }
  if (bVar2) {
    *piVar21 = iVar20 + *piVar22;
    *piVar22 = iVar18 + *piVar22;
  }
  else {
    *piVar22 = (*piVar21 - iVar20) + 1;
    *piVar21 = *piVar21 - iVar18;
  }
  if (cVar6 != '\0') {
    iVar19 = (local_26c * *(int *)(iVar8 + 0x30)) / iVar19;
    if (bVar2) {
      if (bVar23) {
        iVar19 = -iVar19 + *piVar22;
        piVar4 = piVar21;
      }
      else {
        iVar19 = *piVar22 + iVar19 + 1;
        piVar4 = piVar22;
        piVar22 = piVar21;
      }
      if (iVar19 < *piVar21) {
        *piVar4 = *piVar21;
        *piVar22 = iVar19;
      }
      else {
        *piVar22 = *piVar21;
        *piVar4 = iVar19;
      }
    }
    else {
      if (bVar23) {
        iVar19 = *piVar21 + iVar19 + 1;
        piVar4 = piVar21;
        piVar21 = piVar22;
      }
      else {
        iVar19 = -iVar19 + *piVar21;
        piVar4 = piVar22;
      }
      if (iVar19 < *piVar22) {
        *piVar4 = *piVar22;
        *piVar21 = iVar19;
      }
      else {
        *piVar21 = *piVar22;
        *piVar4 = iVar19;
      }
    }
  }
  if ((cVar6 == '\0') && (iVar19 = (*local_24c)(iVar8 + 0x3c), iVar19 < 2)) {
    FUN_00451670(iVar8,0x22,0);
  }
  else {
    FUN_005574b0(auStack_228,iVar8 + 0x3c);
    FUN_00451b9c(auStack_1e4);
    local_1d4 = uVar9;
    FUN_00452616(iVar8,0x20000,auStack_1e4);
    iVar19 = FUN_005574fe(iVar8,0);
    if (iVar12 < iVar13) {
      iVar13 = iVar12;
    }
    if (iVar13 >> 1 < iVar19) {
      iVar19 = iVar13 >> 1;
    }
    iVar13 = FUN_00451598(iVar8 + 0x3c);
    iVar12 = FUN_004515a4(iVar8 + 0x3c);
    if (iVar13 < iVar12) {
      iVar13 = FUN_00451598(iVar8 + 0x3c);
    }
    else {
      iVar13 = FUN_004515a4(iVar8 + 0x3c);
    }
    iVar8 = local_1c8;
    if (iVar13 >> 1 < local_1c8) {
      iVar8 = iVar13 >> 1;
    }
    bVar23 = false;
    if ((bVar2) && ((local_1b5 & 0xf) == 2)) {
      bVar23 = true;
    }
    else if ((!bVar2) && ((local_1b5 & 0xf) == 1)) {
      bVar23 = true;
    }
    if (local_1b4 != 0) {
      bVar23 = true;
    }
    bVar3 = true;
    if ((((iVar14 < 0) || (iVar15 < 0)) || (iVar16 < 0)) || (iVar17 < 0)) {
      bVar3 = false;
    }
    else if (iVar8 < iVar19) {
      iVar13 = FUN_00450f28(auStack_228,&local_248,iVar19);
      if (iVar13 != 0) {
        bVar3 = false;
      }
    }
    else {
      bVar3 = false;
    }
    if ((bool)(bVar23 | bVar3)) {
      if (bVar3) {
        local_19c = 0;
        local_18c = 0;
      }
      else {
        FUN_00439c04(auStack_108,auStack_1e4,0x70);
        local_c0 = 0;
        local_b0 = 0;
        local_e8 = 0;
        local_cd = 0;
        FUN_00451c6e(uVar9,auStack_108,auStack_228);
      }
      local_178 = 0;
      FUN_00439c04(auStack_98,auStack_1e4,0x70);
      local_50 = 0;
      local_40 = 0;
      local_2c = 0;
      FUN_00439c04(&local_238,auStack_228,0x10);
      if (bVar23) {
        if (bVar2) {
          local_238 = iVar14 + local_248;
          local_230 = local_240 - iVar15;
        }
        else {
          local_234 = iVar16 + local_244;
          local_22c = local_23c - iVar17;
        }
        local_7c = 0;
      }
      uVar10 = FUN_0048475e(uVar9,0x10,&local_238);
      FUN_00451c6e(uVar10,auStack_98,&local_238);
      FUN_0048a984(auStack_218);
      if (bVar3) {
        FUN_00439c04(auStack_1fc,&local_248,0x10);
        local_1ec = iVar19;
        FUN_0048a98e(uVar10,auStack_218);
      }
      if (bVar23) {
        FUN_00439c04(auStack_1fc,auStack_228,0x10);
        local_1ec = iVar8;
        FUN_0048a98e(uVar10,auStack_218);
      }
      FUN_00488918(auStack_174);
      local_158 = uVar10;
      FUN_0048895e(uVar9,auStack_174,&local_238);
      FUN_00439c04(auStack_98,auStack_1e4,0x70);
      local_78 = 0;
      local_5d = 0;
      FUN_00451c6e(uVar9,auStack_98,auStack_228);
    }
    else {
      FUN_00451c6e(uVar9,auStack_1e4,auStack_228);
    }
  }
  return;
}

