
undefined4 FUN_005de2ce(int param_1,int param_2)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  byte *pbVar7;
  uint uVar8;
  byte *pbVar9;
  uint uVar10;
  uint uVar11;
  byte *pbVar12;
  uint local_3c;
  uint local_34;
  
  if (*(uint *)(param_2 + 0x84) < param_1 + 10U) {
    ft_validator_run(param_2,8);
  }
  uVar4 = (uint)*(byte *)(param_1 + 3) << 0x10 | (uint)*(byte *)(param_1 + 2) << 0x18 |
          (uint)*(byte *)(param_1 + 4) << 8 | (uint)*(byte *)(param_1 + 5);
  uVar3 = (uint)*(byte *)(param_1 + 7) << 0x10 | (uint)*(byte *)(param_1 + 6) << 0x18 |
          (uint)*(byte *)(param_1 + 8) << 8 | (uint)*(byte *)(param_1 + 9);
  if ((((uint)(*(int *)(param_2 + 0x84) - param_1) < uVar4) || (uVar4 < 10)) ||
     ((uVar4 - 10) / 0xb < uVar3)) {
    ft_validator_run(param_2,8);
  }
  local_34 = 1;
  pbVar7 = (byte *)(param_1 + 10);
  for (local_3c = 0; local_3c < uVar3; local_3c = local_3c + 1) {
    uVar8 = (uint)pbVar7[2] | (uint)pbVar7[1] << 8 | (uint)*pbVar7 << 0x10;
    uVar6 = (uint)pbVar7[6] |
            (uint)pbVar7[4] << 0x10 | (uint)pbVar7[3] << 0x18 | (uint)pbVar7[5] << 8;
    uVar5 = (uint)pbVar7[10] |
            (uint)pbVar7[8] << 0x10 | (uint)pbVar7[7] << 0x18 | (uint)pbVar7[9] << 8;
    if ((uVar4 <= uVar6) || (uVar4 <= uVar5)) {
      ft_validator_run(param_2,8);
    }
    if (uVar8 < local_34) {
      ft_validator_run(param_2,8);
    }
    local_34 = uVar8 + 1;
    if (uVar6 != 0) {
      pbVar9 = (byte *)(param_1 + uVar6);
      uVar6 = 0;
      if (*(byte **)(param_2 + 0x84) < pbVar9 + 4) {
        ft_validator_run(param_2,8);
      }
      pbVar12 = pbVar9 + 4;
      uVar8 = (uint)pbVar9[3] |
              (uint)pbVar9[1] << 0x10 | (uint)*pbVar9 << 0x18 | (uint)pbVar9[2] << 8;
      if ((uint)(*(int *)(param_2 + 0x84) - (int)pbVar12) >> 2 < uVar8) {
        ft_validator_run(param_2,8);
      }
      for (uVar10 = 0; uVar10 < uVar8; uVar10 = uVar10 + 1) {
        uVar11 = (uint)pbVar12[2] | (uint)pbVar12[1] << 8 | (uint)*pbVar12 << 0x10;
        bVar1 = pbVar12[3];
        pbVar12 = pbVar12 + 4;
        if (0x10ffff < bVar1 + uVar11) {
          ft_validator_run(param_2,8);
        }
        if (uVar11 < uVar6) {
          ft_validator_run(param_2,8);
        }
        uVar6 = bVar1 + uVar11 + 1;
      }
    }
    if (uVar5 != 0) {
      pbVar9 = (byte *)(param_1 + uVar5);
      uVar5 = 0;
      if (*(byte **)(param_2 + 0x84) < pbVar9 + 4) {
        ft_validator_run(param_2,8);
      }
      uVar6 = (uint)pbVar9[3] |
              (uint)pbVar9[1] << 0x10 | (uint)*pbVar9 << 0x18 | (uint)pbVar9[2] << 8;
      if ((uint)(*(int *)(param_2 + 0x84) - (int)(pbVar9 + 4)) / 5 < uVar6) {
        ft_validator_run(param_2,8);
      }
      pbVar9 = pbVar9 + 4;
      for (uVar8 = 0; uVar8 < uVar6; uVar8 = uVar8 + 1) {
        uVar10 = (uint)pbVar9[2] | (uint)pbVar9[1] << 8 | (uint)*pbVar9 << 0x10;
        bVar1 = pbVar9[3];
        bVar2 = pbVar9[4];
        if (0x10ffff < uVar10) {
          ft_validator_run(param_2,8);
        }
        if (uVar10 < uVar5) {
          ft_validator_run(param_2,8);
        }
        uVar5 = uVar10 + 1;
        if ((*(char *)(param_2 + 0x88) != '\0') &&
           (*(uint *)(param_2 + 0x90) <= (uint)CONCAT11(bVar1,bVar2))) {
          ft_validator_run(param_2,0x10);
        }
        pbVar9 = pbVar9 + 5;
      }
    }
    pbVar7 = pbVar7 + 0xb;
  }
  return 0;
}

