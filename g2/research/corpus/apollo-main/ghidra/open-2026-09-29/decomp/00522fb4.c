
void FUN_00522fb4(undefined4 param_1,float param_2,float param_3)

{
  undefined4 uVar1;
  int *piVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  float fVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  
  iVar14 = (int)(param_3 * DAT_00523280 + 0.5);
  if (iVar14 < 0x61) {
    if (iVar14 < 0x20) {
      iVar14 = 8;
    }
    else {
      uVar10 = iVar14 + 0xf + ((uint)(iVar14 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
      iVar14 = ((int)(uVar10 + ((uint)((int)uVar10 >> 3) >> 0x1c)) >> 4) << 2;
    }
  }
  else {
    iVar14 = 0x18;
  }
  fVar9 = *(float *)((int)&DAT_005232d0 + iVar14);
  fVar3 = *(float *)((int)&DAT_005232e8 + iVar14);
  iVar4 = 0xe;
  if (1 < iVar14) {
    iVar4 = (iVar14 + -1) * 0x12 + 0xe;
  }
  iVar4 = FUN_00514d2c(iVar4);
  if (-1 < iVar4) {
    iVar4 = FUN_005242cc(param_3);
    iVar5 = FUN_005242cc(param_1);
    iVar12 = 0;
    iVar6 = FUN_005242cc(param_2);
    piVar2 = DAT_005232d0;
    if (1 < iVar14) {
      iVar14 = iVar14 + -1;
      iVar11 = iVar4;
      iVar13 = iVar12;
      fVar16 = DAT_005232c8;
      fVar15 = param_3;
      do {
        fVar17 = fVar3 * fVar15 + fVar9 * fVar16;
        fVar15 = fVar9 * fVar15 - fVar3 * fVar16;
        if ((0.5 <= fVar17 - fVar16) ||
           (iVar4 = iVar11, iVar12 = iVar13, *(char *)(*piVar2 + 0xfa) != '\0')) {
          iVar4 = FUN_005242cc(fVar15);
          iVar12 = FUN_005242cc(fVar17);
          puVar7 = (undefined4 *)FUN_00514aec(9);
          if (puVar7 != (undefined4 *)0x0) {
            *puVar7 = 0x120;
            puVar7[2] = 0x124;
            puVar7[1] = iVar5 - iVar11;
            puVar7[4] = 0x130;
            puVar7[5] = iVar5 - iVar4;
            puVar7[6] = 0x134;
            puVar7[3] = iVar13 + iVar6;
            puVar7[7] = iVar12 + iVar6;
            puVar7[8] = 0x140;
            puVar7[9] = iVar4 + iVar5;
            puVar7[0xb] = iVar12 + iVar6;
            puVar7[0xf] = iVar13 + iVar6;
            uVar8 = DAT_005232cc;
            puVar7[10] = 0x144;
            puVar7[0xc] = 0x150;
            puVar7[0xd] = iVar11 + iVar5;
            puVar7[0xe] = 0x154;
            puVar7[0x10] = uVar8;
            puVar7[0x11] = *(uint *)(*piVar2 + 0x18) | 5;
          }
          puVar7 = (undefined4 *)FUN_00514aec(9);
          if (puVar7 != (undefined4 *)0x0) {
            *puVar7 = 0x120;
            puVar7[2] = 0x124;
            puVar7[1] = iVar5 - iVar4;
            puVar7[4] = 0x130;
            puVar7[5] = iVar5 - iVar11;
            puVar7[3] = iVar6 - iVar12;
            puVar7[8] = 0x140;
            puVar7[9] = iVar11 + iVar5;
            puVar7[10] = 0x144;
            puVar7[0xf] = iVar6 - iVar12;
            uVar8 = DAT_005232cc;
            puVar7[6] = 0x134;
            puVar7[7] = iVar6 - iVar13;
            puVar7[0xb] = iVar6 - iVar13;
            puVar7[0xc] = 0x150;
            puVar7[0xd] = iVar4 + iVar5;
            puVar7[0xe] = 0x154;
            puVar7[0x10] = uVar8;
            puVar7[0x11] = *(uint *)(*piVar2 + 0x18) | 5;
          }
        }
        iVar14 = iVar14 + -1;
        iVar11 = iVar4;
        iVar13 = iVar12;
        fVar16 = fVar17;
      } while (iVar14 != 0);
    }
    uVar8 = FUN_005242cc(param_2 + param_3);
    puVar7 = (undefined4 *)FUN_00514aec(7);
    if (puVar7 != (undefined4 *)0x0) {
      *puVar7 = 0x120;
      puVar7[1] = iVar5;
      puVar7[2] = 0x124;
      puVar7[4] = 0x130;
      puVar7[5] = iVar5 - iVar4;
      puVar7[3] = uVar8;
      puVar7[6] = 0x134;
      puVar7[7] = iVar12 + iVar6;
      puVar7[0xb] = iVar12 + iVar6;
      puVar7[8] = 0x140;
      uVar8 = DAT_005232cc;
      puVar7[9] = iVar4 + iVar5;
      puVar7[10] = 0x144;
      puVar7[0xc] = uVar8;
      uVar10 = *(uint *)(*DAT_005232d0 + 0x18);
      if ((int)(uVar10 << 7) < 0) {
        uVar10 = uVar10 | 0x800000;
      }
      else {
        uVar10 = uVar10 & 0xff7fffff;
      }
      puVar7[0xd] = uVar10 | 4;
    }
    uVar8 = FUN_005242cc(param_2 - param_3);
    puVar7 = (undefined4 *)FUN_00514aec(7);
    if (puVar7 != (undefined4 *)0x0) {
      *puVar7 = 0x120;
      puVar7[1] = iVar5;
      puVar7[2] = 0x124;
      puVar7[4] = 0x130;
      puVar7[5] = iVar5 - iVar4;
      puVar7[8] = 0x140;
      puVar7[10] = 0x144;
      uVar1 = DAT_005232cc;
      puVar7[3] = uVar8;
      puVar7[6] = 0x134;
      puVar7[7] = iVar6 - iVar12;
      puVar7[9] = iVar4 + iVar5;
      puVar7[0xb] = iVar6 - iVar12;
      puVar7[0xc] = uVar1;
      uVar10 = *(uint *)(*DAT_005232d0 + 0x18);
      if ((int)(uVar10 << 7) < 0) {
        uVar10 = uVar10 | 0x800000;
      }
      else {
        uVar10 = uVar10 & 0xff7fffff;
      }
      puVar7[0xd] = uVar10 | 4;
    }
  }
  return;
}

