
undefined4 af_latin_metrics_scale_dim(int param_1,int param_2,byte param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  
  if (param_3 == 0) {
    iVar7 = *(int *)(param_2 + 4);
    iVar8 = *(int *)(param_2 + 0xc);
  }
  else {
    iVar7 = *(int *)(param_2 + 8);
    iVar8 = *(int *)(param_2 + 0x10);
  }
  iVar1 = param_1 + (uint)param_3 * 0x2430;
  piVar9 = (int *)(iVar1 + 0x2c);
  if ((*(int *)(iVar1 + 0x2454) != iVar7) || (*(int *)(iVar1 + 0x2458) != iVar8)) {
    *(int *)(iVar1 + 0x2454) = iVar7;
    *(int *)(iVar1 + 0x2458) = iVar8;
    iVar10 = param_1 + 0x245c;
    iVar2 = 0;
    for (uVar4 = 0; uVar4 < *(uint *)(param_1 + 0x2534); uVar4 = uVar4 + 1) {
      if ((int)((uint)*(byte *)(uVar4 * 0x24 + iVar10 + 0xfc) << 0x1b) < 0) {
        iVar2 = iVar10 + uVar4 * 0x24 + 0xdc;
        break;
      }
    }
    if (iVar2 != 0) {
      uVar4 = FT_MulFix(*(undefined4 *)(iVar2 + 0xc),iVar7);
      uVar6 = (uint)*(ushort *)(*(int *)(*(int *)(param_1 + 4) + 0x58) + 0xc);
      uVar5 = *(uint *)(*(int *)(param_1 + 0x24) + 0xc);
      iVar2 = 0x28;
      if (((uVar5 != 0) && (uVar6 <= uVar5)) && (5 < uVar6)) {
        iVar2 = 0x34;
      }
      uVar5 = iVar2 + uVar4 & 0xffffffc0;
      if ((uVar4 != uVar5) && (param_3 == 1)) {
        iVar3 = FT_MulDiv(iVar7,uVar5,uVar4);
        iVar2 = *(int *)(param_1 + 0x28);
        for (uVar4 = 0; uVar4 < *(uint *)(param_1 + 0x2534); uVar4 = uVar4 + 1) {
          if (iVar2 <= *(int *)(uVar4 * 0x24 + iVar10 + 0xf4)) {
            iVar2 = *(int *)(uVar4 * 0x24 + iVar10 + 0xf4);
          }
          if (iVar2 <= -*(int *)(uVar4 * 0x24 + iVar10 + 0xf8)) {
            iVar2 = -*(int *)(uVar4 * 0x24 + iVar10 + 0xf8);
          }
        }
        iVar10 = FT_MulFix(iVar2,iVar3 - iVar7);
        if (iVar10 < 0) {
          iVar2 = FT_MulFix(iVar2,iVar3 - iVar7);
          uVar4 = -iVar2;
        }
        else {
          uVar4 = FT_MulFix(iVar2,iVar3 - iVar7);
        }
        if ((uVar4 & 0xffffff80) == 0) {
          iVar7 = iVar3;
        }
      }
    }
    *piVar9 = iVar7;
    *(int *)(iVar1 + 0x30) = iVar8;
    if (param_3 == 0) {
      *(int *)(param_1 + 8) = iVar7;
      *(int *)(param_1 + 0x10) = iVar8;
    }
    else {
      *(int *)(param_1 + 0xc) = iVar7;
      *(int *)(param_1 + 0x14) = iVar8;
    }
    for (uVar4 = 0; uVar4 < *(uint *)(iVar1 + 0x34); uVar4 = uVar4 + 1) {
      iVar2 = FT_MulFix(piVar9[uVar4 * 3 + 3],iVar7);
      piVar9[uVar4 * 3 + 4] = iVar2;
      piVar9[uVar4 * 3 + 5] = piVar9[uVar4 * 3 + 4];
    }
    iVar2 = FT_MulFix(*(undefined4 *)(iVar1 + 0xfc),iVar7);
    *(bool *)(iVar1 + 0x100) = iVar2 < 0x28;
    if (param_3 == 1) {
      for (uVar4 = 0; uVar4 < *(uint *)(iVar1 + 0x104); uVar4 = uVar4 + 1) {
        iVar2 = FT_MulFix(piVar9[uVar4 * 9 + 0x37],iVar7);
        piVar9[uVar4 * 9 + 0x38] = iVar8 + iVar2;
        piVar9[uVar4 * 9 + 0x39] = piVar9[uVar4 * 9 + 0x38];
        iVar2 = FT_MulFix(piVar9[uVar4 * 9 + 0x3a],iVar7);
        piVar9[uVar4 * 9 + 0x3b] = iVar8 + iVar2;
        piVar9[uVar4 * 9 + 0x3c] = piVar9[uVar4 * 9 + 0x3b];
        piVar9[uVar4 * 9 + 0x3f] = piVar9[uVar4 * 9 + 0x3f] & 0xfffffffe;
        iVar2 = FT_MulFix(piVar9[uVar4 * 9 + 0x37] - piVar9[uVar4 * 9 + 0x3a],iVar7);
        if (iVar2 + 0x30U < 0x61) {
          iVar10 = iVar2;
          if (iVar2 < 0) {
            iVar10 = -iVar2;
          }
          if (iVar10 < 0x20) {
            iVar10 = 0;
          }
          else if (iVar10 < 0x30) {
            iVar10 = 0x20;
          }
          else {
            iVar10 = 0x40;
          }
          if (iVar2 < 0) {
            iVar10 = -iVar10;
          }
          piVar9[uVar4 * 9 + 0x39] = piVar9[uVar4 * 9 + 0x38] + 0x20U & 0xffffffc0;
          piVar9[uVar4 * 9 + 0x3c] = piVar9[uVar4 * 9 + 0x39] - iVar10;
          piVar9[uVar4 * 9 + 0x3f] = piVar9[uVar4 * 9 + 0x3f] | 1;
        }
      }
      for (uVar4 = 0; uVar4 < *(uint *)(iVar1 + 0x104); uVar4 = uVar4 + 1) {
        if (((int)((uint)*(byte *)(piVar9 + uVar4 * 9 + 0x3f) << 0x1d) < 0) &&
           ((int)((uint)*(byte *)(piVar9 + uVar4 * 9 + 0x3f) << 0x1f) < 0)) {
          for (uVar5 = 0; uVar5 < *(uint *)(iVar1 + 0x104); uVar5 = uVar5 + 1) {
            if ((((-1 < (int)((uint)*(byte *)(piVar9 + uVar5 * 9 + 0x3f) << 0x1d)) &&
                 ((int)((uint)*(byte *)(piVar9 + uVar5 * 9 + 0x3f) << 0x1f) < 0)) &&
                (piVar9[uVar5 * 9 + 0x39] <= piVar9[uVar4 * 9 + 0x3c])) &&
               (piVar9[uVar4 * 9 + 0x39] <= piVar9[uVar5 * 9 + 0x3c])) {
              piVar9[uVar4 * 9 + 0x3f] = piVar9[uVar4 * 9 + 0x3f] & 0xfffffffe;
              break;
            }
          }
        }
      }
    }
  }
  return param_4;
}

