
longlong FUN_005dc600(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  byte bVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  uint uVar7;
  undefined1 *puVar8;
  uint uVar9;
  uint uVar10;
  undefined1 *puVar11;
  uint uVar12;
  undefined1 *puVar13;
  undefined1 *puVar14;
  
  if (*(uint *)(param_2 + 0x84) < param_1 + 4U) {
    ft_validator_run(param_2,8,param_3,param_4,param_2,param_3,param_4);
  }
  uVar7 = (uint)CONCAT11(*(undefined1 *)(param_1 + 2),*(undefined1 *)(param_1 + 3));
  if ((*(uint *)(param_2 + 0x84) < uVar7 + param_1) || (uVar7 < 0x206)) {
    ft_validator_run(param_2,8);
  }
  uVar12 = 0;
  puVar11 = (undefined1 *)(param_1 + 6);
  for (uVar9 = 0; uVar9 < 0x100; uVar9 = uVar9 + 1) {
    uVar3 = *puVar11;
    bVar2 = puVar11[1];
    if ((1 < *(byte *)(param_2 + 0x88)) && ((bVar2 & 7) != 0)) {
      ft_validator_run(param_2,8);
    }
    uVar10 = (uint)(ushort)(CONCAT11(uVar3,bVar2) >> 3);
    if (uVar12 < uVar10) {
      uVar12 = uVar10;
    }
    puVar11 = puVar11 + 2;
  }
  puVar8 = puVar11 + uVar12 * 8 + 8;
  if (*(undefined1 **)(param_2 + 0x84) < puVar8) {
    ft_validator_run(param_2,8);
  }
  for (uVar9 = 0; uVar9 <= uVar12; uVar9 = uVar9 + 1) {
    uVar10 = (uint)CONCAT11(puVar11[2],puVar11[3]);
    uVar3 = puVar11[4];
    uVar4 = puVar11[5];
    puVar14 = puVar11 + 8;
    uVar5 = puVar11[6];
    uVar6 = puVar11[7];
    if (uVar10 != 0) {
      if ((1 < *(byte *)(param_2 + 0x88)) &&
         ((0xff < CONCAT11(*puVar11,puVar11[1]) || (0x100 - CONCAT11(*puVar11,puVar11[1]) < uVar10))
         )) {
        ft_validator_run(param_2,8);
      }
      if (CONCAT11(uVar5,uVar6) != 0) {
        if ((puVar14 + (CONCAT11(uVar5,uVar6) - 2) < puVar8) ||
           ((undefined1 *)(uVar7 + param_1) < puVar14 + (CONCAT11(uVar5,uVar6) - 2) + uVar10 * 2)) {
          ft_validator_run(param_2,9);
        }
        if (*(char *)(param_2 + 0x88) != '\0') {
          puVar11 = puVar14 + uVar10 * 2;
          while (puVar14 < puVar11) {
            puVar13 = puVar14 + 2;
            uVar5 = *puVar14;
            puVar1 = puVar14 + 1;
            puVar14 = puVar13;
            if ((CONCAT11(uVar5,*puVar1) != 0) &&
               (*(uint *)(param_2 + 0x90) <=
                (uint)(ushort)(CONCAT11(uVar3,uVar4) + CONCAT11(uVar5,*puVar1)))) {
              ft_validator_run(param_2,0x10);
            }
          }
        }
      }
    }
    puVar11 = puVar14;
  }
  return (ulonglong)uVar7 << 0x20;
}

