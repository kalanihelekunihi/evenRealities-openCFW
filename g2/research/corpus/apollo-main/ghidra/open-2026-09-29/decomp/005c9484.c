
void FUN_005c9484(undefined4 param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  uint in_fpscr;
  float fVar9;
  int iVar10;
  float fVar11;
  float fVar12;
  undefined1 auStack_78 [16];
  undefined4 local_68;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  byte local_3b;
  int local_38;
  int local_34;
  
  cVar1 = FUN_004516f8(DAT_005c971c,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    iVar3 = *param_2;
    if (iVar2 == 0x1b) {
      iVar2 = FUN_005c9314(iVar3,0);
      if (*(int *)param_2[4] < iVar2) {
        *(int *)param_2[4] = iVar2;
      }
    }
    else if (iVar2 == 0x34) {
      if ((*(int *)(iVar3 + 0x30) != 0) && (*(int *)(iVar3 + 0x2c) != 0)) {
        piVar4 = (int *)param_2[4];
        iVar2 = DAT_005c9718;
        iVar10 = DAT_005c9718;
        for (uVar8 = 0; uVar8 < *(uint *)(iVar3 + 0x30); uVar8 = uVar8 + 1) {
          if ((((int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8) & 0x60000000U) != 0x20000000) ||
             (0x1ffffffe < (int)((int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8) & 0x9fffffffU))
             ) {
            fVar12 = (float)VectorSignedToFloat(iVar2,(byte)(in_fpscr >> 0x16) & 3);
            in_fpscr = in_fpscr & 0xfffffff;
            if (fVar12 < *(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8)) {
              iVar2 = (int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8);
            }
          }
          if ((((int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 4) & 0x60000000U) != 0x20000000
              ) || (0x1ffffffe <
                    (int)((int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 4) & 0x9fffffffU))) {
            fVar12 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
            in_fpscr = in_fpscr & 0xfffffff;
            if (fVar12 < *(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 4)) {
              iVar10 = (int)*(float *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 4);
            }
          }
        }
        *piVar4 = iVar2;
        piVar4[1] = iVar10;
      }
    }
    else if (((iVar2 == 0x1d) && (uVar5 = FUN_00451960(param_2), *(int *)(iVar3 + 0x30) != 0)) &&
            (*(int *)(iVar3 + 0x2c) != 0)) {
      FUN_0043fc2a(iVar3,&local_38);
      iVar2 = FUN_0044e486(iVar3);
      iVar10 = FUN_0044e498(iVar3);
      iVar10 = local_34 - iVar10;
      FUN_005c6fbc(auStack_78);
      local_68 = uVar5;
      FUN_00452b0e(iVar3,0,auStack_78);
      for (uVar8 = 0; uVar8 < *(int *)(iVar3 + 0x30) - 1U; uVar8 = uVar8 + 1) {
        uVar6 = FUN_0043fd9e(iVar3);
        uVar7 = FUN_0043fdda(iVar3);
        fVar12 = (float)VectorSignedToFloat(local_38 - iVar2,(byte)(in_fpscr >> 0x16) & 3);
        local_5c = (float)FUN_005c9344(*(undefined4 *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8),uVar6);
        local_5c = fVar12 + local_5c;
        local_58 = (float)FUN_005c9344(*(undefined4 *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 4),uVar7
                                      );
        fVar12 = (float)VectorSignedToFloat(local_38 - iVar2,(byte)(in_fpscr >> 0x16) & 3);
        local_54 = (float)FUN_005c9344(*(undefined4 *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 8),uVar6
                                      );
        local_54 = fVar12 + local_54;
        fVar12 = (float)FUN_005c9344(*(undefined4 *)(*(int *)(iVar3 + 0x2c) + uVar8 * 8 + 0xc),uVar7
                                    );
        if ((int)((uint)*(byte *)(iVar3 + 0x34) << 0x1f) < 0) {
          fVar9 = (float)VectorSignedToFloat(uVar7,(byte)(in_fpscr >> 0x16) & 3);
          fVar11 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
          local_58 = (fVar9 - local_58) + fVar11;
          fVar9 = (float)VectorSignedToFloat(uVar7,(byte)(in_fpscr >> 0x16) & 3);
          local_50 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
          local_50 = (fVar9 - fVar12) + local_50;
        }
        else {
          fVar9 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
          local_58 = fVar9 + local_58;
          local_50 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
          local_50 = local_50 + fVar12;
        }
        FUN_005c6fea(uVar5,auStack_78);
        local_3b = local_3b & 0xfe;
      }
    }
  }
  return;
}

