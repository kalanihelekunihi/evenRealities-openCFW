
undefined4
af_cjk_hints_link_segments(int param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  
  iVar7 = param_1 + (uint)param_2 * 0x544;
  uVar11 = *(uint *)(iVar7 + 0x34);
  uVar10 = *(int *)(iVar7 + 0x2c) * 0x2c + uVar11;
  cVar1 = *(char *)(iVar7 + 0x44);
  iVar7 = *(int *)(*(int *)(param_1 + 0xabc) + 0x28);
  if (param_2 == 0) {
    uVar5 = *(undefined4 *)(param_1 + 4);
  }
  else {
    uVar5 = *(undefined4 *)(param_1 + 0xc);
  }
  iVar2 = FT_DivFix(0xc0,uVar5);
  for (uVar6 = uVar11; uVar8 = uVar11, uVar6 < uVar10; uVar6 = uVar6 + 0x2c) {
    if (*(char *)(uVar6 + 1) == cVar1) {
      for (; uVar8 < uVar10; uVar8 = uVar8 + 0x2c) {
        if (((uVar8 != uVar6) && ((int)*(char *)(uVar8 + 1) + (int)*(char *)(uVar6 + 1) == 0)) &&
           (iVar12 = (int)*(short *)(uVar8 + 2) - (int)*(short *)(uVar6 + 2), -1 < iVar12)) {
          iVar13 = (int)*(short *)(uVar6 + 6);
          iVar3 = (int)*(short *)(uVar6 + 8);
          if (iVar13 < *(short *)(uVar8 + 6)) {
            iVar13 = (int)*(short *)(uVar8 + 6);
          }
          if (*(short *)(uVar8 + 8) < iVar3) {
            iVar3 = (int)*(short *)(uVar8 + 8);
          }
          iVar3 = iVar3 - iVar13;
          if ((iVar7 << 3) / 0x800 <= iVar3) {
            if ((iVar12 * 8 < *(int *)(uVar6 + 0x1c) * 9) &&
               ((iVar12 * 8 < *(int *)(uVar6 + 0x1c) * 7 || (*(int *)(uVar6 + 0x20) < iVar3)))) {
              *(int *)(uVar6 + 0x1c) = iVar12;
              *(int *)(uVar6 + 0x20) = iVar3;
              *(uint *)(uVar6 + 0x14) = uVar8;
            }
            if ((iVar12 * 8 < *(int *)(uVar8 + 0x1c) * 9) &&
               ((iVar12 * 8 < *(int *)(uVar8 + 0x1c) * 7 || (*(int *)(uVar8 + 0x20) < iVar3)))) {
              *(int *)(uVar8 + 0x1c) = iVar12;
              *(int *)(uVar8 + 0x20) = iVar3;
              *(uint *)(uVar8 + 0x14) = uVar6;
            }
          }
        }
      }
    }
  }
  do {
    if (uVar10 <= uVar8) {
      for (; uVar11 < uVar10; uVar11 = uVar11 + 0x2c) {
        iVar7 = *(int *)(uVar11 + 0x14);
        if (((iVar7 != 0) && (*(uint *)(iVar7 + 0x14) != uVar11)) &&
           ((*(undefined4 *)(uVar11 + 0x14) = 0, *(int *)(iVar7 + 0x1c) < iVar2 ||
            (*(int *)(uVar11 + 0x1c) < *(int *)(iVar7 + 0x1c) * 4)))) {
          *(undefined4 *)(uVar11 + 0x18) = *(undefined4 *)(iVar7 + 0x14);
        }
      }
      return param_4;
    }
    iVar7 = *(int *)(uVar8 + 0x14);
    if ((((iVar7 != 0) && (*(uint *)(iVar7 + 0x14) == uVar8)) &&
        (*(short *)(uVar8 + 2) < *(short *)(iVar7 + 2))) &&
       (uVar6 = uVar11, *(int *)(uVar8 + 0x1c) < iVar2)) {
      for (; uVar6 < uVar10; uVar6 = uVar6 + 0x2c) {
        if ((((*(short *)(uVar6 + 2) <= *(short *)(uVar8 + 2)) && (uVar8 != uVar6)) &&
            ((uVar4 = *(uint *)(uVar6 + 0x14), uVar4 != 0 &&
             ((*(uint *)(uVar4 + 0x14) == uVar6 && (*(short *)(iVar7 + 2) <= *(short *)(uVar4 + 2)))
             )))) && (((*(short *)(uVar8 + 2) != *(short *)(uVar6 + 2) ||
                       (*(short *)(iVar7 + 2) != *(short *)(uVar4 + 2))) &&
                      ((*(int *)(uVar8 + 0x1c) < *(int *)(uVar6 + 0x1c) &&
                       (*(int *)(uVar6 + 0x1c) < *(int *)(uVar8 + 0x1c) * 4)))))) {
          uVar9 = uVar11;
          if (*(int *)(uVar8 + 0x20) < *(int *)(uVar6 + 0x20) * 3) {
            *(undefined4 *)(iVar7 + 0x14) = 0;
            *(undefined4 *)(uVar8 + 0x14) = *(undefined4 *)(iVar7 + 0x14);
            break;
          }
          for (; uVar9 < uVar10; uVar9 = uVar9 + 0x2c) {
            if (*(uint *)(uVar9 + 0x14) == uVar6) {
              *(undefined4 *)(uVar9 + 0x14) = 0;
              *(int *)(uVar9 + 0x18) = iVar7;
            }
            else if (*(uint *)(uVar9 + 0x14) == uVar4) {
              *(undefined4 *)(uVar9 + 0x14) = 0;
              *(uint *)(uVar9 + 0x18) = uVar8;
            }
          }
        }
      }
    }
    uVar8 = uVar8 + 0x2c;
  } while( true );
}

