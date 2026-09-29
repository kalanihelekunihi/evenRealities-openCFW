
void af_hint_normal_stem(int param_1,int param_2,int param_3,int param_4,char param_5)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  
  uVar5 = 0x40;
  if (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1d)) {
    if (((int)((uint)*(byte *)(param_2 + 0xc) << 0x1f) < 0) &&
       ((int)((uint)*(byte *)(param_3 + 0xc) << 0x1f) < 0)) {
      if (param_5 == '\x01') {
        uVar5 = 0x37;
      }
      else {
        uVar5 = 0x31;
      }
    }
    else if (param_5 == '\x01') {
      uVar5 = 0x3d;
    }
    else {
      uVar5 = 0x3b;
    }
  }
  uVar1 = af_cjk_compute_stem_width
                    (param_1,param_5,*(int *)(param_3 + 4) - *(int *)(param_2 + 4),
                     *(undefined1 *)(param_2 + 0xc),*(undefined1 *)(param_3 + 0xc),param_4);
  uVar6 = (param_4 + (*(int *)(param_3 + 4) + *(int *)(param_2 + 4)) / 2) - (int)uVar1 / 2;
  iVar3 = uVar6 - (uVar6 & 0xffffffc0);
  iVar4 = (uVar1 + uVar6) - (uVar1 + uVar6 & 0xffffffc0);
  iVar8 = 0x40 - iVar3;
  iVar2 = 0;
  if ((iVar3 != 0) && (iVar4 != 0)) {
    if ((int)uVar5 < (int)uVar1) {
      if ((0x3f < uVar5) ||
         ((((iVar3 < (int)uVar5 && (iVar8 < (int)uVar5)) && (iVar4 < (int)uVar5)) &&
          (0x40 - iVar4 < (int)uVar5)))) {
        uVar7 = uVar1 & 0x3f;
        if (uVar7 < 0x20) {
          if ((iVar8 <= (int)uVar7) || (iVar4 <= (int)uVar7)) goto LAB_005a746a;
        }
        else {
          uVar7 = 0x40 - uVar5;
        }
        iVar3 = iVar8 - uVar7;
        iVar2 = uVar5 - iVar4;
        if ((int)(uVar5 - iVar8) <= iVar3) {
          iVar3 = -(uVar5 - iVar8);
        }
        if ((int)(iVar4 - uVar7) <= iVar2) {
          iVar2 = -(iVar4 - uVar7);
        }
        iVar4 = iVar2;
        if (iVar2 < 0) {
          iVar4 = -iVar2;
        }
        iVar8 = iVar3;
        if (iVar3 < 0) {
          iVar8 = -iVar3;
        }
        if (iVar8 <= iVar4) {
          iVar2 = iVar3;
        }
      }
    }
    else if ((iVar4 < (int)uVar1) && (iVar2 = iVar8, iVar4 < iVar8)) {
      iVar2 = -iVar4;
    }
  }
LAB_005a746a:
  if (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1d)) {
    if (iVar2 < 0xf) {
      if (iVar2 < -0xe) {
        iVar2 = -0xe;
      }
    }
    else {
      iVar2 = 0xe;
    }
  }
  iVar2 = iVar2 + uVar6;
  if (*(int *)(param_2 + 4) < *(int *)(param_3 + 4)) {
    *(int *)(param_2 + 8) = iVar2;
    *(uint *)(param_3 + 8) = uVar1 + iVar2;
  }
  else {
    *(uint *)(param_2 + 8) = uVar1 + iVar2;
    *(int *)(param_3 + 8) = iVar2;
  }
  return;
}

