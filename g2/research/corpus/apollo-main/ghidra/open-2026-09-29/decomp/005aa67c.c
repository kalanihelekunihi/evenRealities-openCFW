
undefined8
af_latin_compute_stem_width
          (int param_1,byte param_2,uint param_3,int param_4,int param_5,int param_6)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  bool bVar5;
  bool bVar6;
  
  iVar3 = *(int *)(param_1 + 0xabc) + (uint)param_2 * 0x2430;
  bVar6 = param_2 != 1;
  if (((int)((uint)*(byte *)(param_1 + 0xab8) << 0x1d) < 0) && (*(char *)(iVar3 + 0x100) == '\0')) {
    bVar5 = (int)param_3 < 0;
    uVar4 = param_3;
    if (bVar5) {
      uVar4 = -param_3;
    }
    if (((!bVar6) && (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1e))) ||
       ((bVar6 && (-1 < (int)((uint)*(byte *)(param_1 + 0xab8) << 0x1f))))) {
      if (((-1 < param_6 << 0x1e) || (bVar6)) || (uVar1 = uVar4, 0xbf < (int)uVar4)) {
        if (param_5 << 0x1f < 0) {
          if ((int)uVar4 < 0x50) {
            uVar4 = 0x40;
          }
        }
        else if ((int)uVar4 < 0x38) {
          uVar4 = 0x38;
        }
        uVar1 = uVar4;
        if (*(int *)(iVar3 + 0x34) != 0) {
          iVar2 = uVar4 - *(int *)(iVar3 + 0x3c);
          if (iVar2 < 0) {
            iVar2 = -iVar2;
          }
          if (iVar2 < 0x28) {
            uVar1 = *(uint *)(iVar3 + 0x3c);
            if ((int)*(uint *)(iVar3 + 0x3c) < 0x30) {
              uVar1 = 0x30;
            }
          }
          else if ((int)uVar4 < 0xc0) {
            uVar1 = uVar4 & 0x3f;
            uVar4 = uVar4 & 0xffffffc0;
            if (uVar1 < 10) {
              uVar1 = uVar1 + uVar4;
            }
            else if (uVar1 < 0x20) {
              uVar1 = uVar4 + 10;
            }
            else if (uVar1 < 0x36) {
              uVar1 = uVar4 + 0x36;
            }
            else {
              uVar1 = uVar1 + uVar4;
            }
          }
          else {
            iVar3 = 0;
            if (((0 < (int)param_3) && (0 < param_4)) || (((int)param_3 < 0 && (param_4 < 0)))) {
              uVar1 = (uint)*(ushort *)
                             (*(int *)(*(int *)(*(int *)(param_1 + 0xabc) + 4) + 0x58) + 0xc);
              iVar2 = param_4;
              if ((9 < uVar1) && (iVar2 = iVar3, uVar1 < 0x1e)) {
                iVar2 = (int)((0x1e - uVar1) * param_4) / 0x14;
              }
              iVar3 = iVar2;
              if (iVar3 < 0) {
                iVar3 = -iVar3;
              }
            }
            uVar1 = (uVar4 - iVar3) + 0x20 & 0xffffffc0;
          }
        }
      }
    }
    else {
      iVar3 = af_latin_snap_width(iVar3 + 0x38,*(undefined4 *)(iVar3 + 0x34));
      if (bVar6) {
        if ((int)((uint)*(byte *)(param_1 + 0xab8) << 0x1c) < 0) {
          if (iVar3 < 0x40) {
            uVar1 = 0x40;
          }
          else {
            uVar1 = iVar3 + 0x20U & 0xffffffc0;
          }
        }
        else if (iVar3 < 0x30) {
          uVar1 = iVar3 + 0x40 >> 1;
        }
        else if (iVar3 < 0x80) {
          uVar1 = iVar3 + 0x16U & 0xffffffc0;
          iVar3 = uVar1 - uVar4;
          if (iVar3 < 0) {
            iVar3 = -iVar3;
          }
          if ((0xf < iVar3) && (uVar1 = uVar4, (int)uVar4 < 0x30)) {
            uVar1 = (int)(uVar4 + 0x40) >> 1;
          }
        }
        else {
          uVar1 = iVar3 + 0x20U & 0xffffffc0;
        }
      }
      else if (iVar3 < 0x40) {
        uVar1 = 0x40;
      }
      else {
        uVar1 = iVar3 + 0x10U & 0xffffffc0;
      }
    }
    param_3 = uVar1;
    if (bVar5) {
      param_3 = -param_3;
    }
  }
  return CONCAT44(param_4,param_3);
}

