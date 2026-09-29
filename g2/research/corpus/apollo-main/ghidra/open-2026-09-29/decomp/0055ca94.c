
undefined4 FUN_0055ca94(uint *param_1,char *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    uVar5 = 2;
  }
  else if (((param_1 == (uint *)0x0) || (param_2 == (char *)0x0)) || (7 < param_1[1])) {
    uVar5 = 6;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar5 = 7;
  }
  else {
    uVar8 = param_1[1];
    *(char *)(param_1 + 2) = *param_2;
    iVar1 = DAT_0055cf38;
    *(undefined4 *)(DAT_0055cf38 + uVar8 * 0x1000 + 0x104) = 0x1010;
    uVar3 = DAT_0055d270;
    uVar2 = DAT_0055d268;
    uVar6 = DAT_0055d260;
    if (*param_2 == '\0') {
      if (3 < (byte)param_2[8]) {
        return 6;
      }
      if (DAT_0055d24c <= *(uint *)(param_2 + 4)) {
        return 6;
      }
      uVar6 = FUN_0055bf64(*(undefined4 *)(param_2 + 4),((byte)param_2[8] & 3) >> 1);
      *(uint *)(iVar1 + uVar8 * 0x1000 + 0x280) = (byte)param_2[8] & 3;
    }
    else {
      if (*param_2 != '\x01') {
        return 5;
      }
      uVar7 = *(uint *)(param_2 + 4);
      if (uVar7 == DAT_0055d258) {
        *(undefined4 *)(iVar1 + uVar8 * 0x1000 + 0x2c0) = DAT_0055d264;
      }
      else if (uVar7 == DAT_0055d25c) {
        *(undefined4 *)(iVar1 + uVar8 * 0x1000 + 0x2c0) = DAT_0055d26c;
        uVar6 = uVar2;
      }
      else {
        if (uVar7 != DAT_0055d250) {
          return 6;
        }
        *(undefined4 *)(iVar1 + uVar8 * 0x1000 + 0x2c0) = DAT_0055d274;
        uVar6 = uVar3;
      }
    }
    *(uint *)(iVar1 + uVar8 * 0x1000 + 0x118) = uVar6 | 1;
    param_1[0x219] = DAT_0055d250 / *(uint *)(param_2 + 4);
    param_1[0x218] = 1000;
    param_1[3] = *(uint *)(param_2 + 0xc);
    param_1[4] = *(uint *)(param_2 + 0x10);
    if (param_1[3] != 0) {
      *(bool *)(param_1 + 0x229) = param_1[3] + param_1[4] * 4 < DAT_0055d254;
      param_1[0x216] = ((param_1[4] - 8) * 4) / 0x60;
      if (0x100 < param_1[0x216]) {
        param_1[0x216] = 0x100;
      }
    }
    for (bVar4 = 0; bVar4 < 4; bVar4 = bVar4 + 1) {
      *(undefined1 *)((int)param_1 + bVar4 + 0x8a0) = 0;
    }
    uVar5 = 0;
  }
  return uVar5;
}

