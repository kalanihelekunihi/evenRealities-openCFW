
/* WARNING: Removing unreachable block (ram,0x10004bf2) */

uint FUN_10004b50(uint param_1)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  byte *pbVar5;
  uint uVar6;
  int local_20;
  int iStack_1c;
  uint *puStack_18;
  
  if (param_1 - 7 < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10004b62. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar2 = (*(code *)(*(uint *)(PTR_PTR_10004b64 + (param_1 - 7) * 4) & 0xfffffffe))();
    return uVar2;
  }
  iVar3 = FUN_1000452c(param_1,&local_20);
  if (iVar3 == 0) {
    uVar4 = (uint)*(char *)(local_20 + 6);
    uVar2 = 0;
    if (uVar4 != 0xffffffff) {
      if ((((param_1 < 10) && ((1 << (param_1 & 0x3f) & 0x243U) != 0)) && (uVar4 + 1 != 0)) &&
         ((*puStack_18 >> (uVar4 + 1 & 0x3f) & 1) != 0)) {
        uVar2 = 32000;
      }
      else if ((*puStack_18 >> (uVar4 & 0x3f) & 1) == 0) {
        uVar2 = 0xbb8000;
        if (8 < param_1) {
          return 0xbb8000;
        }
        if ((param_1 & 0xfffffffb) == 2) {
          return 0xbb8000;
        }
      }
      else {
        uVar2 = 0;
        if ((*puStack_18 >> (uVar4 & 0x3f) & 1) != 0) {
          if ((uRam0000008c & 1) == 0) {
            uVar2 = 0;
          }
          else {
            uVar6 = (*(uint *)(DAT_10004d28 + 0x1c) & 0x3f) + 1;
            uVar2 = (*(uint *)(DAT_10004d28 + 0x30) & 0x1f) >> 4;
            uVar4 = (*(uint *)(DAT_10004d28 + 0x20) | (*(uint *)(DAT_10004d28 + 0x24) & 0x1f) << 8)
                    + 1;
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
            uVar2 = (uVar6 * iVar3) / uVar4;
            if (uVar2 - 16000 < 32000) {
              uVar2 = 32000;
            }
            else if (DAT_10004d30 < uVar2 + DAT_10004d2c) {
              if (DAT_10004d38 < uVar2 + DAT_10004d34) {
                return 0xffffffff;
              }
              uVar2 = 0x1f4000;
            }
            else {
              uVar2 = 0xfa000;
            }
            uVar2 = (uVar4 * (uVar2 / uVar6)) / (((*(uint *)(DAT_10004d28 + 0x28) & 7) + 1) * 2);
          }
          if (*(byte **)(local_20 + 0xc) != (byte *)0x0) {
            lVar1 = (ulonglong)(*(uint *)((uint)**(byte **)(local_20 + 0xc) + iStack_1c) & 0xffffff)
                    * (ulonglong)uVar2;
            uVar2 = (int)((ulonglong)lVar1 >> 0x20) << 7 | (uint)lVar1 >> 0x19;
          }
        }
      }
      pbVar5 = *(byte **)(local_20 + 8);
      if ((pbVar5 != (byte *)0x0) &&
         (uVar4 = *(uint *)((uint)*pbVar5 + iStack_1c) >> (pbVar5[1] & 0x3f) &
                  (uint)*(ushort *)(pbVar5 + 2), uVar4 != 0)) {
        return uVar2 / (uVar4 + 1);
      }
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

