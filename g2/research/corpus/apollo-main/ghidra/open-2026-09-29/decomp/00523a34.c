
void FUN_00523a34(undefined4 *param_1,int param_2,int param_3)

{
  bool bVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  
  if (param_2 < 3) {
    return;
  }
  uVar8 = param_1[param_3 * 2 + 1];
  uVar9 = param_1[param_3 * 2];
  uVar10 = param_1[param_3 + 1];
  uVar11 = param_1[param_3];
  uVar12 = param_1[1];
  uVar3 = FUN_005242cc(*param_1);
  uVar12 = FUN_005242cc(uVar12);
  uVar11 = FUN_005242cc(uVar11);
  uVar10 = FUN_005242cc(uVar10);
  uVar9 = FUN_005242cc(uVar9);
  uVar8 = FUN_005242cc(uVar8);
  puVar4 = (undefined4 *)FUN_00514aec(7);
  if (puVar4 != (undefined4 *)0x0) {
    *puVar4 = 0x120;
    puVar4[2] = 0x124;
    puVar4[1] = uVar3;
    puVar4[3] = uVar12;
    puVar4[4] = 0x130;
    puVar4[5] = uVar11;
    puVar4[6] = 0x134;
    puVar4[7] = uVar10;
    puVar4[8] = 0x140;
    puVar4[10] = 0x144;
    uVar3 = DAT_00523bf4;
    puVar4[9] = uVar9;
    puVar4[0xb] = uVar8;
    puVar4[0xc] = uVar3;
    uVar5 = *(uint *)(*DAT_00523bf0 + 0x18);
    if ((int)(uVar5 << 7) < 0) {
      uVar5 = uVar5 | 0x800000;
    }
    else {
      uVar5 = uVar5 & 0xff7fffff;
    }
    puVar4[0xd] = uVar5 | 4;
  }
  uVar3 = DAT_00523bf4;
  piVar2 = DAT_00523bf0;
  iVar7 = 1;
  if (1 < param_2 + -2) {
    iVar6 = 3;
    do {
      uVar11 = param_1[param_3 * iVar6 + 1];
      uVar12 = FUN_005242cc(param_1[param_3 * iVar6]);
      uVar11 = FUN_005242cc(uVar11);
      puVar4 = (undefined4 *)FUN_00514aec(3);
      if (puVar4 != (undefined4 *)0x0) {
        *puVar4 = 0x130;
        puVar4[1] = uVar12;
        puVar4[2] = 0x134;
        puVar4[3] = uVar11;
        puVar4[4] = uVar3;
        uVar5 = *(uint *)(*piVar2 + 0x18);
        if ((int)(uVar5 << 7) < 0) {
          uVar5 = uVar5 | 0x800000;
        }
        else {
          uVar5 = uVar5 & 0xff7fffff;
        }
        puVar4[5] = uVar5 | 4;
      }
      bVar1 = true;
      iVar6 = iVar7;
      while( true ) {
        iVar7 = iVar6 + 1;
        if (param_2 + -2 <= iVar7) {
          return;
        }
        iVar6 = iVar6 + 3;
        if (!bVar1) break;
        uVar11 = param_1[param_3 * iVar6 + 1];
        uVar12 = FUN_005242cc(param_1[param_3 * iVar6]);
        uVar11 = FUN_005242cc(uVar11);
        puVar4 = (undefined4 *)FUN_00514aec(3);
        if (puVar4 != (undefined4 *)0x0) {
          *puVar4 = 0x140;
          puVar4[1] = uVar12;
          puVar4[2] = 0x144;
          puVar4[3] = uVar11;
          puVar4[4] = uVar3;
          uVar5 = *(uint *)(*piVar2 + 0x18);
          if ((int)(uVar5 << 7) < 0) {
            uVar5 = uVar5 | 0x800000;
          }
          else {
            uVar5 = uVar5 & 0xff7fffff;
          }
          puVar4[5] = uVar5 | 4;
        }
        bVar1 = false;
        iVar6 = iVar7;
      }
    } while( true );
  }
  return;
}

