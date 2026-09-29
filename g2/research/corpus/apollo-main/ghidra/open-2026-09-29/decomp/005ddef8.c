
longlong FUN_005ddef8(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  byte *pbVar9;
  uint uVar10;
  
  if (*(uint *)(param_2 + 0x84) < param_1 + 0x10U) {
    ft_validator_run(param_2,8);
  }
  uVar5 = (uint)*(byte *)(param_1 + 7) |
          (uint)*(byte *)(param_1 + 5) << 0x10 | (uint)*(byte *)(param_1 + 4) << 0x18 |
          (uint)*(byte *)(param_1 + 6) << 8;
  uVar7 = (uint)*(byte *)(param_1 + 0xf) |
          (uint)*(byte *)(param_1 + 0xd) << 0x10 | (uint)*(byte *)(param_1 + 0xc) << 0x18 |
          (uint)*(byte *)(param_1 + 0xe) << 8;
  if ((((uint)(*(int *)(param_2 + 0x84) - param_1) < uVar5) || (uVar5 < 0x10)) ||
     ((uVar5 - 0x10) / 0xc < uVar7)) {
    ft_validator_run(param_2,8);
  }
  pbVar9 = (byte *)(param_1 + 0x10);
  uVar5 = 0;
  for (uVar6 = 0; uVar6 < uVar7; uVar6 = uVar6 + 1) {
    uVar10 = (uint)pbVar9[3] |
             (uint)pbVar9[1] << 0x10 | (uint)*pbVar9 << 0x18 | (uint)pbVar9[2] << 8;
    uVar8 = (uint)pbVar9[7] |
            (uint)pbVar9[5] << 0x10 | (uint)pbVar9[4] << 0x18 | (uint)pbVar9[6] << 8;
    bVar1 = pbVar9[8];
    bVar2 = pbVar9[9];
    bVar3 = pbVar9[10];
    bVar4 = pbVar9[0xb];
    if (uVar8 < uVar10) {
      ft_validator_run(param_2,8);
    }
    if ((uVar6 != 0) && (uVar10 <= uVar5)) {
      ft_validator_run(param_2,8);
    }
    if ((*(char *)(param_2 + 0x88) != '\0') &&
       (*(uint *)(param_2 + 0x90) <=
        ((uint)bVar4 | (uint)bVar2 << 0x10 | (uint)bVar1 << 0x18 | (uint)bVar3 << 8))) {
      ft_validator_run(param_2,0x10);
    }
    pbVar9 = pbVar9 + 0xc;
    uVar5 = uVar8;
  }
  return (ulonglong)param_4 << 0x20;
}

