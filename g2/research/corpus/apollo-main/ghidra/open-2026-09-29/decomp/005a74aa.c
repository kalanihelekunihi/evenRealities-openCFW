
undefined8 af_cjk_hint_edges(int param_1,byte param_2)

{
  bool bVar1;
  int iVar2;
  short *psVar3;
  int iVar4;
  short *psVar5;
  short *psVar6;
  short *psVar7;
  short *psVar8;
  short *psVar9;
  int iVar10;
  int iVar11;
  short *psVar12;
  undefined4 local_28;
  
  iVar2 = param_1 + (uint)param_2 * 0x544;
  psVar12 = *(short **)(iVar2 + 0x40);
  psVar3 = psVar12 + *(int *)(iVar2 + 0x38) * 0x16;
  psVar7 = (short *)0x0;
  local_28 = 0;
  iVar11 = 0;
  bVar1 = false;
  iVar2 = 0;
  for (psVar9 = psVar12; psVar6 = psVar12, psVar9 < psVar3; psVar9 = psVar9 + 0x16) {
    if (-1 < (int)((uint)*(byte *)(psVar9 + 6) << 0x1d)) {
      iVar4 = *(int *)(psVar9 + 10);
      psVar8 = *(short **)(psVar9 + 0xc);
      psVar6 = psVar9;
      if (((iVar4 == 0) && (psVar6 = (short *)0x0, psVar8 != (short *)0x0)) &&
         (*(int *)(psVar8 + 10) != 0)) {
        iVar4 = *(int *)(psVar8 + 10);
        psVar6 = psVar8;
        psVar8 = psVar9;
      }
      if (psVar6 != (short *)0x0) {
        *(undefined4 *)(psVar6 + 4) = *(undefined4 *)(iVar4 + 8);
        *(byte *)(psVar6 + 6) = *(byte *)(psVar6 + 6) | 4;
        if ((psVar8 != (short *)0x0) && (*(int *)(psVar8 + 10) == 0)) {
          af_cjk_align_linked_edge(param_1,param_2,psVar6,psVar8);
          *(byte *)(psVar8 + 6) = *(byte *)(psVar8 + 6) | 4;
        }
        if (psVar7 == (short *)0x0) {
          psVar7 = psVar9;
        }
      }
    }
  }
  for (; psVar6 < psVar3; psVar6 = psVar6 + 0x16) {
    if (-1 < (int)((uint)*(byte *)(psVar6 + 6) << 0x1d)) {
      psVar9 = *(short **)(psVar6 + 0xc);
      if (psVar9 == (short *)0x0) {
        iVar11 = iVar11 + 1;
      }
      else if ((bVar1) &&
              ((*(int *)(psVar6 + 4) < iVar2 + 0x40 || (*(int *)(psVar9 + 4) < iVar2 + 0x40)))) {
        iVar11 = iVar11 + 1;
      }
      else if (*(int *)(psVar9 + 10) == 0) {
        if (psVar9 < psVar6) {
          af_cjk_align_linked_edge(param_1,param_2,psVar9,psVar6);
          *(byte *)(psVar6 + 6) = *(byte *)(psVar6 + 6) | 4;
          bVar1 = true;
          iVar2 = *(int *)(psVar6 + 4);
        }
        else {
          if ((param_2 == 1) || (psVar7 != (short *)0x0)) {
            af_hint_normal_stem(param_1,psVar6,psVar9,local_28,param_2);
          }
          else {
            local_28 = af_hint_normal_stem(param_1,psVar6,psVar9,0,0);
          }
          *(byte *)(psVar6 + 6) = *(byte *)(psVar6 + 6) | 4;
          *(byte *)(psVar9 + 6) = *(byte *)(psVar9 + 6) | 4;
          bVar1 = true;
          iVar2 = *(int *)(psVar9 + 4);
          psVar7 = psVar6;
        }
      }
      else {
        af_cjk_align_linked_edge(param_1,param_2,psVar9,psVar6);
        *(byte *)(psVar6 + 6) = *(byte *)(psVar6 + 6) | 4;
      }
    }
  }
  iVar4 = ((int)psVar3 - (int)psVar12) / 0x2c;
  if ((param_2 == 0) && ((iVar4 == 6 || (iVar4 == 0xc)))) {
    if (iVar4 == 6) {
      psVar6 = psVar12 + 0x2c;
      psVar9 = psVar12 + 0x58;
      psVar7 = psVar12;
    }
    else {
      psVar7 = psVar12 + 0x16;
      psVar6 = psVar12 + 0x6e;
      psVar9 = psVar12 + 0xc6;
    }
    iVar10 = (*(int *)(psVar6 + 2) - *(int *)(psVar7 + 2)) -
             (*(int *)(psVar9 + 2) - *(int *)(psVar6 + 2));
    if (iVar10 < 0) {
      iVar10 = -iVar10;
    }
    if ((((*(short **)(psVar7 + 0xc) == psVar7 + 0x16) &&
         (*(short **)(psVar6 + 0xc) == psVar6 + 0x16)) &&
        (*(short **)(psVar9 + 0xc) == psVar9 + 0x16)) && (iVar10 < 8)) {
      iVar10 = *(int *)(psVar7 + 4) + *(int *)(psVar9 + 4) + *(int *)(psVar6 + 4) * -2;
      *(int *)(psVar9 + 4) = *(int *)(psVar9 + 4) - iVar10;
      if (*(int *)(psVar9 + 0xc) != 0) {
        *(int *)(*(int *)(psVar9 + 0xc) + 8) = *(int *)(*(int *)(psVar9 + 0xc) + 8) - iVar10;
      }
      if (iVar4 == 0xc) {
        *(int *)(psVar12 + 0xb4) = *(int *)(psVar12 + 0xb4) - iVar10;
        *(int *)(psVar12 + 0xf6) = *(int *)(psVar12 + 0xf6) - iVar10;
      }
      *(byte *)(psVar9 + 6) = *(byte *)(psVar9 + 6) | 4;
      if (*(int *)(psVar9 + 0xc) != 0) {
        *(byte *)(*(int *)(psVar9 + 0xc) + 0xc) = *(byte *)(*(int *)(psVar9 + 0xc) + 0xc) | 4;
      }
    }
  }
  psVar7 = psVar12;
  if (iVar11 != 0) {
    for (; psVar7 < psVar3; psVar7 = psVar7 + 0x16) {
      if ((-1 < (int)((uint)*(byte *)(psVar7 + 6) << 0x1d)) && (*(int *)(psVar7 + 0xe) != 0)) {
        af_cjk_align_serif_edge(param_1,*(undefined4 *)(psVar7 + 0xe),psVar7);
        *(byte *)(psVar7 + 6) = *(byte *)(psVar7 + 6) | 4;
        iVar11 = iVar11 + -1;
      }
    }
    psVar7 = psVar12;
    if (iVar11 != 0) {
      for (; psVar7 < psVar3; psVar7 = psVar7 + 0x16) {
        psVar9 = psVar7;
        if (-1 < (int)((uint)*(byte *)(psVar7 + 6) << 0x1d)) {
          do {
            psVar8 = psVar9;
            psVar9 = psVar8 + -0x16;
            psVar6 = psVar7;
            if (psVar9 < psVar12) break;
          } while (-1 < (int)((uint)*(byte *)(psVar8 + -0x10) << 0x1d));
          do {
            psVar5 = psVar6;
            psVar6 = psVar5 + 0x16;
            if (psVar3 <= psVar6) break;
          } while (-1 < (int)((uint)*(byte *)(psVar5 + 0x1c) << 0x1d));
          if ((psVar12 <= psVar9) || (psVar6 < psVar3)) {
            if (psVar9 < psVar12) {
              af_cjk_align_serif_edge(param_1,psVar6,psVar7);
            }
            else if (psVar6 < psVar3) {
              if (*psVar6 == *psVar9) {
                *(undefined4 *)(psVar7 + 4) = *(undefined4 *)(psVar8 + -0x12);
              }
              else {
                iVar11 = FT_MulDiv((int)*psVar7 - (int)*psVar9,
                                   *(int *)(psVar5 + 0x1a) - *(int *)(psVar8 + -0x12),
                                   (int)*psVar6 - (int)*psVar9);
                *(int *)(psVar7 + 4) = iVar11 + *(int *)(psVar8 + -0x12);
              }
            }
            else {
              af_cjk_align_serif_edge(param_1,psVar9,psVar7);
            }
          }
        }
      }
    }
  }
  return CONCAT44(psVar3,iVar2);
}

