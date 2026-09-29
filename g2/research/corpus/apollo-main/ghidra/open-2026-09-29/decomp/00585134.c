
undefined8 FUN_00585134(int *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint extraout_r2;
  uint uVar4;
  byte *pbVar5;
  byte *pbVar6;
  uint uVar7;
  byte *pbVar8;
  bool bVar9;
  bool bVar10;
  
  pbVar5 = (byte *)*param_1;
  uVar7 = 0;
  while (iVar2 = FUN_004d58ae(*pbVar5), iVar2 != 0) {
    pbVar5 = pbVar5 + 1;
  }
  bVar1 = *pbVar5;
  if (bVar1 == 0x2d) {
    uVar7 = 8;
  }
  if (bVar1 == 0x2d || bVar1 == 0x2b) {
    pbVar5 = pbVar5 + 1;
  }
  bVar1 = *pbVar5;
  if ((bVar1 | 0x20) == 0x6e) {
    bVar1 = pbVar5[1] | 0x20;
    bVar9 = bVar1 == 0x61;
    if (bVar9) {
      bVar1 = pbVar5[2] | 0x20;
    }
    if (bVar9 && bVar1 == 0x6e) {
      pbVar6 = pbVar5 + 3;
      uVar7 = 4;
      pbVar5 = pbVar6;
      if (*pbVar6 == 0x28) {
        do {
          do {
            pbVar8 = pbVar5;
            pbVar5 = pbVar8 + 1;
            bVar1 = *pbVar5;
            iVar2 = FUN_00541ba8((uint)bVar1);
          } while (iVar2 != 0);
        } while ((bVar1 - 0x30 < 10) || (*pbVar5 == 0x5f));
        if (*pbVar5 == 0x29) {
          pbVar6 = pbVar8 + 2;
        }
      }
    }
    else {
      pbVar6 = (byte *)*param_1;
      uVar7 = 0;
    }
  }
  else {
    if ((bVar1 | 0x20) != 0x69) {
      bVar9 = bVar1 == 0x30;
      if (bVar9) {
        bVar1 = pbVar5[1] | 0x20;
      }
      if (bVar9 && bVar1 == 0x78) {
        pbVar6 = pbVar5 + 2;
        if (*pbVar6 == 0x2e) {
          pbVar6 = pbVar5 + 3;
        }
        uVar3 = (uint)*pbVar6;
        bVar9 = 5 < uVar3 - 0x61;
        uVar4 = extraout_r2;
        if (bVar9) {
          uVar4 = uVar3 - 0x41;
        }
        bVar10 = bVar9 && 5 < uVar4;
        if (bVar9 && 5 < uVar4) {
          bVar10 = 9 < uVar3 - 0x30;
        }
        if (!bVar10) {
          pbVar5 = pbVar5 + 2;
          uVar7 = uVar7 | 2;
          goto LAB_0058524e;
        }
      }
      uVar7 = uVar7 | 1;
      goto LAB_0058524e;
    }
    bVar1 = pbVar5[1] | 0x20;
    bVar9 = bVar1 == 0x6e;
    if (bVar9) {
      bVar1 = pbVar5[2] | 0x20;
    }
    if (bVar9 && bVar1 == 0x66) {
      pbVar6 = pbVar5 + 3;
      bVar1 = *pbVar6 | 0x20;
      uVar7 = uVar7 | 3;
      bVar9 = bVar1 == 0x69;
      if (bVar9) {
        bVar1 = pbVar5[4] | 0x20;
      }
      if (bVar9 && bVar1 == 0x6e) {
        bVar1 = pbVar5[5] | 0x20;
        bVar9 = bVar1 == 0x69;
        if (bVar9) {
          bVar1 = pbVar5[6] | 0x20;
        }
        if ((bVar9 && bVar1 == 0x74) && ((pbVar5[7] | 0x20) == 0x79)) {
          pbVar6 = pbVar5 + 8;
        }
      }
    }
    else {
      pbVar6 = (byte *)*param_1;
      uVar7 = 0;
    }
  }
  pbVar5 = pbVar6;
  if (param_2 != (int *)0x0) {
    *param_2 = (int)pbVar6;
  }
LAB_0058524e:
  *param_1 = (int)pbVar5;
  return CONCAT44(param_4,uVar7);
}

