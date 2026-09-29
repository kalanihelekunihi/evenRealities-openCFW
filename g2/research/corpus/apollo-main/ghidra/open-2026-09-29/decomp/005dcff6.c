
uint FUN_005dcff6(int *param_1,uint *param_2,char param_3)

{
  ushort uVar1;
  undefined1 *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  undefined1 *puVar16;
  int iVar17;
  undefined1 *puVar18;
  uint uVar19;
  uint uVar20;
  bool bVar21;
  
  iVar11 = *param_1;
  puVar2 = (undefined1 *)(*(int *)(iVar11 + 0x1fc) + *(int *)(iVar11 + 0x200));
  uVar10 = *param_2;
  uVar9 = 0;
  uVar1 = CONCAT11(*(undefined1 *)(param_1[4] + 6),*(undefined1 *)(param_1[4] + 7));
  uVar8 = uVar1 & 0xfffffffe;
  if ((uVar1 & 0xfffe) == 0) {
    return 0;
  }
  uVar3 = (uint)(uVar1 >> 1);
  uVar20 = 0xffff;
  if (param_3 != '\0') {
    uVar10 = uVar10 + 1;
  }
  uVar4 = 0;
  uVar5 = uVar3;
  uVar6 = uVar3;
  while (uVar7 = uVar5, uVar4 < uVar7) {
    uVar6 = uVar7 + uVar4 >> 1;
    iVar15 = param_1[4] + uVar6 * 2;
    puVar16 = (undefined1 *)(iVar15 + 0xe);
    uVar20 = (uint)CONCAT11(*puVar16,*(undefined1 *)(iVar15 + 0xf));
    uVar12 = (uint)CONCAT11(puVar16[uVar8 + 2],puVar16[uVar8 + 3]);
    uVar5 = uVar6;
    if (uVar12 <= uVar10) {
      if (uVar10 <= uVar20) {
        puVar16 = puVar16 + uVar8 + 2 + uVar8;
        iVar15 = (int)CONCAT11(*puVar16,puVar16[1]);
        puVar16 = puVar16 + uVar8;
        uVar5 = (uint)CONCAT11(*puVar16,puVar16[1]);
        if ((((uVar3 - 1 <= uVar6) && (uVar12 == 0xffff)) && (uVar20 == 0xffff)) &&
           ((uVar5 != 0 && (puVar2 < puVar16 + uVar5 + 2)))) {
          iVar15 = 1;
          uVar5 = 0;
        }
        if ((int)((uint)*(byte *)(param_1 + 5) << 0x1e) < 0) {
          uVar4 = uVar6;
          uVar7 = uVar6;
          if (uVar5 == 0xffff) {
            uVar7 = uVar6 + 1;
          }
          goto LAB_005dd14c;
        }
        if (uVar5 != 0xffff) goto LAB_005dd2b6;
        break;
      }
      uVar4 = uVar6 + 1;
      uVar5 = uVar7;
    }
  }
LAB_005dd34a:
  if (param_3 != '\0') {
    if ((uVar20 < uVar10) && (uVar6 = uVar6 + 1, uVar6 == uVar3)) {
      uVar9 = 0;
    }
    else {
      iVar11 = FUN_005dc99c(param_1,uVar6);
      if (iVar11 == 0) {
        param_1[6] = uVar10;
        if (uVar9 == 0) {
          param_1[6] = uVar10;
          FUN_005dca46(param_1);
          uVar9 = param_1[7];
        }
        else {
          param_1[7] = uVar9;
        }
        if (uVar9 != 0) {
          *param_2 = param_1[6];
        }
      }
      else if (uVar9 != 0) {
        *param_2 = uVar10;
      }
    }
  }
  return uVar9;
LAB_005dd14c:
  if (uVar4 == 0) goto LAB_005dd178;
  iVar17 = param_1[4] + uVar4 * 2;
  puVar18 = (undefined1 *)(iVar17 + 0xc);
  uVar13 = (uint)CONCAT11(*puVar18,*(undefined1 *)(iVar17 + 0xd));
  if (uVar13 < uVar10) goto LAB_005dd178;
  uVar12 = (uint)CONCAT11(puVar18[uVar8 + 2],puVar18[uVar8 + 3]);
  puVar16 = puVar18 + uVar8 + 2 + uVar8;
  iVar15 = (int)CONCAT11(*puVar16,puVar16[1]);
  puVar16 = puVar16 + uVar8;
  uVar5 = (uint)CONCAT11(*puVar16,puVar16[1]);
  if (uVar5 != 0xffff) {
    uVar7 = uVar4 - 1;
  }
  uVar4 = uVar4 - 1;
  uVar20 = uVar13;
  goto LAB_005dd14c;
LAB_005dd178:
  if (uVar7 == uVar6 + 1) {
    bVar21 = uVar4 != uVar6;
    uVar7 = uVar6;
    uVar4 = uVar6;
    if (bVar21) {
      iVar17 = param_1[4] + uVar6 * 2;
      puVar18 = (undefined1 *)(iVar17 + 0xe);
      puVar16 = puVar18 + uVar8 + 2 + uVar8;
      iVar15 = (int)CONCAT11(*puVar16,puVar16[1]);
      puVar16 = puVar16 + uVar8;
      uVar5 = (uint)CONCAT11(*puVar16,puVar16[1]);
      uVar12 = (uint)CONCAT11(puVar18[uVar8 + 2],puVar18[uVar8 + 3]);
      uVar20 = (uint)CONCAT11(*puVar18,*(undefined1 *)(iVar17 + 0xf));
    }
    while (uVar13 = uVar4 + 1, uVar13 < uVar3) {
      iVar17 = param_1[4] + uVar13 * 2;
      puVar18 = (undefined1 *)(iVar17 + 0xe);
      uVar14 = (uint)CONCAT11(*puVar18,*(undefined1 *)(iVar17 + 0xf));
      puVar16 = puVar18 + uVar8 + 2;
      uVar19 = (uint)CONCAT11(*puVar16,puVar18[uVar8 + 3]);
      if (uVar10 < uVar19) break;
      puVar16 = puVar16 + uVar8;
      iVar15 = (int)CONCAT11(*puVar16,puVar16[1]);
      puVar16 = puVar16 + uVar8;
      uVar5 = (uint)CONCAT11(*puVar16,puVar16[1]);
      uVar12 = uVar19;
      uVar20 = uVar14;
      uVar4 = uVar13;
      if (uVar5 != 0xffff) {
        uVar7 = uVar13;
      }
    }
    bVar21 = uVar7 == uVar6;
    uVar6 = uVar4;
    if (bVar21) goto LAB_005dd34a;
  }
  uVar6 = uVar7;
  if (uVar7 != uVar4) {
    iVar15 = param_1[4] + uVar7 * 2;
    puVar16 = (undefined1 *)(iVar15 + 0xe);
    uVar20 = (uint)CONCAT11(*puVar16,*(undefined1 *)(iVar15 + 0xf));
    uVar12 = (uint)CONCAT11(puVar16[uVar8 + 2],puVar16[uVar8 + 3]);
    puVar16 = puVar16 + uVar8 + 2 + uVar8;
    iVar15 = (int)CONCAT11(*puVar16,puVar16[1]);
    puVar16 = puVar16 + uVar8;
    uVar5 = (uint)CONCAT11(*puVar16,puVar16[1]);
  }
LAB_005dd2b6:
  if (uVar5 == 0) {
    uVar9 = iVar15 + uVar10 & 0xffff;
    if ((param_3 != '\0') && (*(uint *)(iVar11 + 0x10) <= uVar9)) {
      uVar9 = 0;
      if (((int)(iVar15 + uVar10) < 0) && (-1 < (int)(iVar15 + uVar20))) {
        uVar10 = -iVar15;
      }
      else if (((int)(iVar15 + uVar10) < 0x10000) && (0xffff < (int)(iVar15 + uVar20))) {
        uVar10 = 0x10000 - iVar15;
      }
    }
  }
  else {
    puVar16 = puVar16 + uVar5 + (uVar10 - uVar12) * 2;
    if ((param_3 == '\0') || (puVar16 <= puVar2)) {
      uVar9 = 0;
      if ((CONCAT11(*puVar16,puVar16[1]) != 0) &&
         (uVar9 = iVar15 + (uint)CONCAT11(*puVar16,puVar16[1]) & 0xffff,
         *(uint *)(iVar11 + 0x10) <= uVar9)) {
        uVar9 = 0;
      }
    }
  }
  goto LAB_005dd34a;
}

