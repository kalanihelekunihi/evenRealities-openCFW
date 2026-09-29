
longlong FUN_005dd584(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  byte *pbVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  
  if (*(uint *)(param_2 + 0x84) < param_1 + 0x2010U) {
    ft_validator_run(param_2,8,param_3,param_4,param_2,param_3,param_4);
  }
  uVar5 = (uint)*(byte *)(param_1 + 7) |
          (uint)*(byte *)(param_1 + 5) << 0x10 | (uint)*(byte *)(param_1 + 4) << 0x18 |
          (uint)*(byte *)(param_1 + 6) << 8;
  if (((uint)(*(int *)(param_2 + 0x84) - param_1) < uVar5) || (uVar5 < 0x2010)) {
    ft_validator_run(param_2,8);
  }
  uVar5 = param_1 + 0xc;
  uVar6 = (uint)*(byte *)(param_1 + 0x200d) << 0x10 | (uint)*(byte *)(param_1 + 0x200c) << 0x18 |
          (uint)*(byte *)(param_1 + 0x200e) << 8 | (uint)*(byte *)(param_1 + 0x200f);
  if ((uint)(*(int *)(param_2 + 0x84) - (param_1 + 0x2010)) / 0xc < uVar6) {
    ft_validator_run(param_2,8);
  }
  uVar9 = 0;
  pbVar11 = (byte *)(param_1 + 0x2010);
  for (uVar14 = 0; uVar14 < uVar6; uVar14 = uVar14 + 1) {
    uVar7 = (uint)pbVar11[1] << 0x10 | (uint)*pbVar11 << 0x18;
    uVar12 = (uint)pbVar11[3] | uVar7 | (uint)pbVar11[2] << 8;
    uVar8 = (uint)pbVar11[5] << 0x10 | (uint)pbVar11[4] << 0x18;
    uVar13 = (uint)pbVar11[7] | uVar8 | (uint)pbVar11[6] << 8;
    bVar1 = pbVar11[8];
    bVar2 = pbVar11[9];
    bVar3 = pbVar11[10];
    bVar4 = pbVar11[0xb];
    if (uVar13 < uVar12) {
      ft_validator_run(param_2,8);
    }
    if ((uVar14 != 0) && (uVar12 <= uVar9)) {
      ft_validator_run(param_2,8);
    }
    if (*(char *)(param_2 + 0x88) != '\0') {
      if ((*(uint *)(param_2 + 0x90) < uVar13 - uVar12) ||
         (*(int *)(param_2 + 0x90) - (uVar13 - uVar12) <=
          ((uint)bVar4 | (uint)bVar2 << 0x10 | (uint)bVar1 << 0x18 | (uint)bVar3 << 8))) {
        ft_validator_run(param_2,0x10);
      }
      iVar10 = (uVar13 - uVar12) + 1;
      if (uVar7 == 0) {
        if (uVar8 != 0) {
          ft_validator_run(param_2,8);
        }
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          if ((*(byte *)(uVar5 + ((uVar12 & 0xffff) >> 3)) & 0x80U >> (uVar12 & 7)) != 0) {
            ft_validator_run(param_2,8);
          }
          uVar12 = uVar12 + 1;
        }
      }
      else {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          if ((*(byte *)(uVar5 + (uVar12 >> 0x13)) & 0x80U >> (uVar12 >> 0x10 & 7)) == 0) {
            ft_validator_run(param_2,8);
          }
          if ((*(byte *)(uVar5 + ((uVar12 & 0xffff) >> 3)) & 0x80U >> (uVar12 & 7)) == 0) {
            ft_validator_run(param_2,8);
          }
          uVar12 = uVar12 + 1;
        }
      }
    }
    uVar9 = uVar13;
    pbVar11 = pbVar11 + 0xc;
  }
  return (ulonglong)uVar5 << 0x20;
}

