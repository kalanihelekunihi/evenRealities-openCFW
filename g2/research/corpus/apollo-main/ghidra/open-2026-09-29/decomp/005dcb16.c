
uint FUN_005dcb16(int param_1,int param_2)

{
  sbyte sVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  undefined1 *puVar11;
  undefined1 *puVar12;
  uint uVar13;
  uint uVar14;
  undefined1 *puVar15;
  uint local_4c;
  undefined1 *local_48;
  undefined1 *local_44;
  undefined1 *local_40;
  uint local_3c;
  
  uVar13 = 0;
  if (*(uint *)(param_2 + 0x84) < param_1 + 4U) {
    ft_validator_run(param_2,8);
  }
  local_4c = (uint)CONCAT11(*(undefined1 *)(param_1 + 2),*(undefined1 *)(param_1 + 3));
  if (*(uint *)(param_2 + 0x84) < param_1 + local_4c) {
    if (*(char *)(param_2 + 0x88) != '\0') {
      ft_validator_run(param_2,8);
    }
    local_4c = *(int *)(param_2 + 0x84) - param_1;
  }
  if (local_4c < 0x10) {
    ft_validator_run(param_2,8);
  }
  uVar4 = CONCAT11(*(undefined1 *)(param_1 + 6),*(undefined1 *)(param_1 + 7));
  if ((1 < *(byte *)(param_2 + 0x88)) && ((int)((uint)uVar4 << 0x1f) < 0)) {
    ft_validator_run(param_2,8);
  }
  uVar8 = (uint)(uVar4 >> 1);
  if (local_4c < uVar8 * 8 + 0x10) {
    ft_validator_run(param_2,8);
  }
  if (1 < *(byte *)(param_2 + 0x88)) {
    uVar4 = CONCAT11(*(undefined1 *)(param_1 + 8),*(undefined1 *)(param_1 + 9));
    sVar1 = *(sbyte *)(param_1 + 0xb);
    uVar5 = CONCAT11(*(undefined1 *)(param_1 + 0xc),*(undefined1 *)(param_1 + 0xd));
    if ((int)((uint)(uVar5 | uVar4) << 0x1f) < 0) {
      ft_validator_run(param_2,8);
    }
    uVar6 = (uint)(uVar4 >> 1);
    if ((((uVar8 < uVar6) || (uVar6 << 1 < uVar8)) || ((uVar5 >> 1) + uVar6 != uVar8)) ||
       (uVar6 != 1 << sVar1)) {
      ft_validator_run(param_2,8);
    }
  }
  local_44 = (undefined1 *)(param_1 + 0xe);
  local_40 = (undefined1 *)(param_1 + uVar8 * 2 + 0x10);
  local_48 = local_40 + uVar8 * 2;
  puVar11 = local_48 + uVar8 * 2;
  if ((1 < *(byte *)(param_2 + 0x88)) &&
     (CONCAT11(local_44[uVar8 * 2 + -2],local_44[uVar8 * 2 + -1]) != -1)) {
    ft_validator_run(param_2,8);
  }
  local_3c = 0;
  puVar12 = puVar11;
  uVar6 = 0;
  for (uVar7 = 0; uVar7 < uVar8; uVar7 = uVar7 + 1) {
    uVar9 = (uint)CONCAT11(*local_40,local_40[1]);
    uVar10 = (uint)CONCAT11(*local_44,local_44[1]);
    uVar2 = *local_48;
    uVar3 = local_48[1];
    uVar14 = (uint)CONCAT11(*puVar12,puVar12[1]);
    if (uVar10 < uVar9) {
      ft_validator_run(param_2,8);
    }
    if ((uVar9 <= uVar6) && (uVar7 != 0)) {
      if (*(char *)(param_2 + 0x88) == '\0') {
        if ((uVar9 < local_3c) || (uVar10 < uVar6)) {
          uVar13 = uVar13 | 1;
        }
        else {
          uVar13 = uVar13 | 2;
        }
      }
      else {
        ft_validator_run(param_2,8);
      }
    }
    if ((uVar14 == 0) || (uVar14 == 0xffff)) {
      if ((uVar14 == 0xffff) &&
         ((((1 < *(byte *)(param_2 + 0x88) || (uVar7 != uVar8 - 1)) || (uVar9 != 0xffff)) ||
          (uVar10 != 0xffff)))) {
        ft_validator_run(param_2,8);
      }
    }
    else {
      puVar15 = puVar12 + uVar14;
      if (*(char *)(param_2 + 0x88) == '\0') {
        if ((((uVar7 != uVar8 - 1) || (uVar9 != 0xffff)) || (uVar10 != 0xffff)) &&
           ((puVar15 < puVar11 + uVar8 * 2 ||
            (*(undefined1 **)(param_2 + 0x84) < puVar15 + (uVar10 - uVar9) * 2 + 2)))) {
          ft_validator_run(param_2,8);
        }
      }
      else if ((puVar15 < puVar11 + uVar8 * 2) ||
              ((undefined1 *)(param_1 + local_4c) < puVar15 + (uVar10 - uVar9) * 2 + 2)) {
        ft_validator_run(param_2,8);
      }
      uVar6 = uVar9;
      if (*(char *)(param_2 + 0x88) != '\0') {
        for (; uVar6 < uVar10; uVar6 = uVar6 + 1) {
          if ((CONCAT11(*puVar15,puVar15[1]) != 0) &&
             (*(uint *)(param_2 + 0x90) <=
              (uint)(ushort)(CONCAT11(uVar2,uVar3) + CONCAT11(*puVar15,puVar15[1])))) {
            ft_validator_run(param_2,0x10);
          }
          puVar15 = puVar15 + 2;
        }
      }
    }
    puVar12 = puVar12 + 2;
    uVar6 = uVar10;
    local_48 = local_48 + 2;
    local_44 = local_44 + 2;
    local_40 = local_40 + 2;
    local_3c = uVar9;
  }
  return uVar13;
}

