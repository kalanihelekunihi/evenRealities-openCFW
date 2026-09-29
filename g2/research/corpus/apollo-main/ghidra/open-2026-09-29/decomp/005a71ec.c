
uint af_cjk_compute_stem_width(int param_1,byte param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  bool bVar4;
  bool bVar5;
  
  iVar3 = *(int *)(param_1 + 0xabc) + (uint)param_2 * 0x1c58;
  bVar5 = param_2 == 1;
  if (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1d)) {
    return param_3;
  }
  bVar4 = (int)param_3 < 0;
  if (bVar4) {
    param_3 = -param_3;
  }
  if (((bVar5) && (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1e))) ||
     ((!bVar5 && (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1f))))) {
    if (*(int *)(iVar3 + 0x34) != 0) {
      if ((int)(param_3 - *(int *)(iVar3 + 0x3c)) < 0) {
        iVar1 = *(int *)(iVar3 + 0x3c) - param_3;
      }
      else {
        iVar1 = param_3 - *(int *)(iVar3 + 0x3c);
      }
      if (iVar1 < 0x28) {
        param_3 = *(uint *)(iVar3 + 0x3c);
        if ((int)param_3 < 0x30) {
          param_3 = 0x30;
        }
        goto LAB_005a7314;
      }
    }
    if ((int)param_3 < 0x36) {
      param_3 = (int)(0x36 - param_3) / 2 + param_3;
    }
    else if ((int)param_3 < 0xc0) {
      uVar2 = param_3 & 0x3f;
      param_3 = param_3 & 0xffffffc0;
      if (uVar2 < 10) {
        param_3 = uVar2 + param_3;
      }
      else if (uVar2 < 0x16) {
        param_3 = param_3 + 10;
      }
      else if (uVar2 < 0x2a) {
        param_3 = uVar2 + param_3;
      }
      else if (uVar2 < 0x36) {
        param_3 = param_3 + 0x36;
      }
      else {
        param_3 = uVar2 + param_3;
      }
    }
  }
  else {
    iVar3 = af_cjk_snap_width(iVar3 + 0x38,*(undefined4 *)(iVar3 + 0x34));
    if (bVar5) {
      if (iVar3 < 0x40) {
        param_3 = 0x40;
      }
      else {
        param_3 = iVar3 + 0x10U & 0xffffffc0;
      }
    }
    else if ((int)((uint)*(byte *)(param_1 + 0xab8) << 0x1c) < 0) {
      if (iVar3 < 0x40) {
        param_3 = 0x40;
      }
      else {
        param_3 = iVar3 + 0x20U & 0xffffffc0;
      }
    }
    else if (iVar3 < 0x30) {
      param_3 = iVar3 + 0x40 >> 1;
    }
    else if (iVar3 < 0x80) {
      param_3 = iVar3 + 0x16U & 0xffffffc0;
    }
    else {
      param_3 = iVar3 + 0x20U & 0xffffffc0;
    }
  }
LAB_005a7314:
  if (bVar4) {
    param_3 = -param_3;
  }
  return param_3;
}

