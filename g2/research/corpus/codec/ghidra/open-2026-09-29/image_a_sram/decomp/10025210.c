
/* WARNING: Restarted to delay deadcode elimination for space: stack */

uint gx8002_clock_frequency(uint param_1)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iStack_24;
  int iStack_20;
  uint *puStack_1c;
  
  if (param_1 - 7 < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10025222. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar2 = (*(code *)(*(uint *)(iRam10025224 + (param_1 - 7) * 4) & 0xfffffffe))();
    return uVar2;
  }
  iVar3 = __module_get_info(param_1,&iStack_24);
  if (iVar3 == 0) {
    uVar4 = (uint)*(char *)(iStack_24 + 6);
    uVar2 = 0;
    if (uVar4 != 0xffffffff) {
      uVar2 = 0;
      if ((param_1 < 10) && ((1 << (param_1 & 0x3f) & 0x243U) != 0)) {
        uVar2 = uVar4 + 1;
      }
      if ((uVar2 == 0) || ((*puStack_1c >> (uVar2 & 0x3f) & 1) == 0)) {
        if ((*puStack_1c >> (uVar4 & 0x3f) & 1) == 0) {
          uVar2 = 0xbb8000;
          if ((uRam0000008c & 0x40000) != 0) {
            uVar2 = 0xfa000;
          }
          if (8 < param_1) {
            return uVar2;
          }
          if ((param_1 & 0xfffffffb) == 2) {
            return uVar2;
          }
        }
        else {
          uVar2 = 0;
          if ((*puStack_1c >> (uVar4 & 0x3f) & 1) != 0) {
            if ((uRam0000008c & 1) == 0) {
              uVar2 = 0;
            }
            else {
              uVar5 = (*(uint *)(DAT_100253b8 + 0x1c) & 0x3f) + 1;
              uVar2 = (*(uint *)(DAT_100253b8 + 0x30) & 0x1f) >> 4;
              uVar4 = ((*(uint *)(DAT_100253b8 + 0x24) & 0x1f) << 8 | *(uint *)(DAT_100253b8 + 0x20)
                      ) + 1;
              if (uVar2 == 2) {
                iVar3 = 0x5208000;
              }
              else if (uVar2 == 3) {
                iVar3 = 0;
              }
              else {
                iVar3 = 0;
                if (uVar2 != 1) {
                  iVar3 = 0x3a98000;
                }
              }
              uVar2 = (uVar5 * iVar3) / uVar4;
              if (uVar2 - 16000 < 32000) {
                uVar2 = 32000;
              }
              else if (DAT_100253c0 < uVar2 + DAT_100253bc) {
                if (DAT_100253c8 < uVar2 + DAT_100253c4) {
                  return 0xffffffff;
                }
                uVar2 = 0x1f4000;
              }
              else {
                uVar2 = 0xfa000;
              }
              uVar2 = (uVar4 * (uVar2 / uVar5)) / (((*(uint *)(DAT_100253b8 + 0x28) & 7) + 1) * 2);
            }
            if ((*(byte **)(iStack_24 + 0xc) != (byte *)0x0) &&
               (uVar4 = *(uint *)((uint)**(byte **)(iStack_24 + 0xc) + iStack_20),
               (uVar4 & 0x8000000) == 0)) {
              lVar1 = (ulonglong)(uVar4 & 0xffffff) * (ulonglong)uVar2;
              uVar2 = (uint)lVar1 >> 0x19 | (int)((ulonglong)lVar1 >> 0x20) << 7;
            }
          }
        }
      }
      else {
        uVar2 = 32000;
      }
      uVar4 = __module_get_div_isra_1(iStack_24,iStack_20);
      if (uVar4 != 0) {
        uVar2 = uVar2 / uVar4;
      }
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

