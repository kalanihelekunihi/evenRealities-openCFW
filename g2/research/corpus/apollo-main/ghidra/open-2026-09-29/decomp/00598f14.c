
uint FUN_00598f14(int param_1,uint param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  byte bVar3;
  float *pfVar4;
  uint *puVar5;
  uint uVar6;
  float *pfVar7;
  uint *puVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint in_fpscr;
  float fVar13;
  float fVar14;
  
  uVar6 = 0;
  if (((int)param_2 < 1) || (4 < (int)param_2)) {
    return param_2;
  }
  iVar2 = 0;
  puVar5 = (uint *)(*(int *)(DAT_00599048 + param_1 * 4) + param_2 * 0x10 + -0x10);
  puVar8 = puVar5;
  do {
    uVar12 = *puVar8 & 0xff;
    uVar9 = (*puVar8 & 0xffff) >> 8;
    fVar13 = *(float *)(param_3 + uVar12 * 4);
    if (uVar12 + 1 < uVar9) {
      uVar10 = uVar9 - (uVar12 + 1);
      if ((uVar10 & 3) != 0) {
        do {
          loopEnd();
        } while( true );
      }
      if (uVar10 >> 2 != 0) {
        do {
          loopEnd();
        } while( true );
      }
    }
    if (iVar2 == 0) {
      iVar11 = 0x14;
    }
    else {
      iVar11 = 10;
    }
    fVar14 = (float)VectorSignedToFloat((uVar9 - uVar12) * iVar11,(byte)(in_fpscr >> 0x16) & 3);
    uVar9 = in_fpscr & 0xfffffff | (uint)(fVar13 < fVar14) << 0x1f;
    in_fpscr = uVar9 | (uint)(NAN(fVar13) || NAN(fVar14)) << 0x1c;
    if ((byte)(uVar9 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
      uVar6 = iVar2 + 1;
    }
    iVar2 = iVar2 + 1;
    puVar8 = puVar8 + 1;
  } while (iVar2 < (int)param_2);
  bVar3 = (byte)uVar6;
  uVar6 = uVar6 & 0xff;
  if ((int)uVar6 < (int)param_2) {
    uVar9 = (uint)(byte)puVar5[uVar6];
    iVar11 = *(int *)(DAT_0059904c + param_1 * 0x10 + uVar6 * 4);
    bVar1 = false;
    iVar2 = (uVar9 - iVar11) + 1;
    pfVar7 = (float *)(param_3 + iVar2 * 4);
    pfVar4 = (float *)(param_3 + (iVar2 - iVar11) * 4);
    do {
      if ((int)(uVar9 + 1) < iVar2) {
        bVar3 = (byte)param_2;
        break;
      }
      if ((int)((uint)(*(float *)(uVar6 * 4 + 0x5990bc) * *pfVar7 < *pfVar4) << 0x1f) < 0) {
        bVar1 = true;
      }
      iVar2 = iVar2 + 1;
      pfVar4 = pfVar4 + 1;
      pfVar7 = pfVar7 + 1;
    } while (!bVar1);
  }
  return (uint)bVar3;
}

