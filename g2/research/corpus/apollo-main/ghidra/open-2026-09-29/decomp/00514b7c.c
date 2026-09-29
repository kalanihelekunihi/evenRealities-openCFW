
void FUN_00514b7c(int param_1)

{
  int *piVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_20;
  undefined4 local_1c;
  int local_18;
  int local_14;
  
  if (param_1 == 0) {
    FUN_004b127c(0x2000);
    return;
  }
  iVar6 = *(int *)(param_1 + 0x14);
  uVar2 = *(uint *)(param_1 + 0x18) & 0x20;
  if (uVar2 == 0) {
    iVar4 = param_1;
    if (iVar6 != 0) {
      do {
        iVar6 = *(int *)(iVar4 + 8);
        if (-1 < (int)((uint)*(byte *)(iVar4 + 0x18) << 0x1d)) {
          if ((iVar4 != 0) && (-1 < *(int *)(iVar4 + 0x18) << 0x1c)) {
            if (*(int *)(iVar4 + 0x18) << 0x1a < 0) {
              iVar6 = *(int *)(iVar4 + 0x30) * *(int *)(iVar4 + 0x2c);
              local_14 = *(int *)(iVar4 + 0xc) + iVar6 * 4;
              local_18 = *(int *)(iVar4 + 8) + iVar6 * 4;
              local_20 = *(int *)(iVar4 + 0x2c) << 2;
              local_1c = *(undefined4 *)(iVar4 + 4);
              FUN_005140ea(&local_20);
              *(uint *)(iVar4 + 0x18) = *(uint *)(iVar4 + 0x18) | 8;
            }
            else {
              FUN_005140ea(iVar4);
              *(uint *)(iVar4 + 0x18) = *(uint *)(iVar4 + 0x18) | 8;
            }
          }
          break;
        }
        if (*(int *)(iVar4 + 0x20) != 0) {
          *(undefined4 *)(iVar6 + *(int *)(iVar4 + 0x10) * 4 + -4) =
               *(undefined4 *)(*(int *)(iVar4 + 0x20) + 0x14);
        }
        if (iVar4 == 0) {
          FUN_004b127c(0x2000);
        }
        else {
          uVar2 = *(uint *)(iVar4 + 0x18) & 0xfffffff7;
          *(uint *)(iVar4 + 0x18) = uVar2;
          if ((int)(uVar2 << 0x1a) < 0) {
            iVar5 = *(int *)(iVar4 + 0x30) * *(int *)(iVar4 + 0x2c);
            local_14 = *(int *)(iVar4 + 0xc) + iVar5 * 4;
            local_18 = iVar6 + iVar5 * 4;
            local_20 = *(int *)(iVar4 + 0x2c) << 2;
            local_1c = *(undefined4 *)(iVar4 + 4);
            FUN_005140ea(&local_20);
          }
          else {
            FUN_005140ea(iVar4);
          }
          *(uint *)(iVar4 + 0x18) = *(uint *)(iVar4 + 0x18) | 8;
        }
        piVar1 = (int *)(iVar4 + 0x20);
        iVar4 = *piVar1;
      } while (*piVar1 != 0);
      uVar3 = FUN_00523dba(param_1,*(undefined4 *)(param_1 + 0x14));
      *(undefined4 *)(param_1 + 0x1c) = uVar3;
    }
  }
  else {
    iVar4 = *(int *)(param_1 + 0x2c);
    iVar6 = iVar6 - iVar4 * (iVar6 / iVar4);
    if (iVar6 != 0) {
      iVar4 = *(int *)(param_1 + 0x30) * iVar4;
      iVar5 = *(int *)(param_1 + 0xc) + iVar4 * 4;
      if (-1 < (int)(*(uint *)(param_1 + 0x18) << 0x1c)) {
        if (uVar2 == 0) {
          FUN_005140ea(param_1);
        }
        else {
          local_18 = *(int *)(param_1 + 8) + iVar4 * 4;
          local_20 = *(int *)(param_1 + 0x2c) << 2;
          local_1c = *(undefined4 *)(param_1 + 4);
          local_14 = iVar5;
          FUN_005140ea(&local_20);
        }
        *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | 8;
      }
      iVar4 = FUN_0051403c(0x148);
      *(int *)(param_1 + 0x38) = iVar4;
      if (*(int *)(param_1 + 0x28) + -2 < *(int *)(param_1 + 0x34) - iVar4) {
        FUN_00514026(iVar4 + 1);
      }
      uVar3 = FUN_00523ce0(iVar5,iVar6);
      *(undefined4 *)(param_1 + 0x34) = uVar3;
      uVar2 = *(int *)(param_1 + 0x30) + 1;
      if (uVar2 < *(uint *)(param_1 + 0x28)) {
        iVar6 = uVar2 * *(int *)(param_1 + 0x2c);
      }
      else {
        iVar6 = 0;
        uVar2 = 0;
      }
      *(int *)(param_1 + 0x14) = iVar6;
      *(uint *)(param_1 + 0x30) = uVar2;
      return;
    }
  }
  return;
}

