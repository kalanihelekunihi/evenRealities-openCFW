
undefined4 FUN_005d1f26(int param_1,int param_2,int param_3)

{
  byte *pbVar1;
  byte *pbVar2;
  byte *pbVar3;
  int *piVar4;
  byte bVar5;
  int iVar6;
  uint uVar7;
  
  *(int *)(param_1 + 0x46c) = param_1 + 0x6c;
  *(int *)(param_1 + 0x53c) = param_1 + 0x470;
  *(undefined1 *)(param_1 + 0x40) = 0;
  *(int *)(param_1 + 0x474) = param_2;
  pbVar1 = (byte *)(param_2 + param_3);
  *(byte **)(param_1 + 0x478) = pbVar1;
  pbVar2 = *(byte **)(param_1 + 0x474);
  *(byte **)(param_1 + 0x470) = pbVar2;
  while( true ) {
    if (pbVar1 <= pbVar2) {
      return 0xa0;
    }
    piVar4 = *(int **)(param_1 + 0x46c);
    bVar5 = 0;
    iVar6 = 0;
    pbVar3 = pbVar2 + 1;
    uVar7 = (uint)*pbVar2;
    if (uVar7 == 1) {
      return 0xa0;
    }
    if (uVar7 - 3 < 9) {
      return 0xa0;
    }
    if (uVar7 == 0xc) {
      if (pbVar1 <= pbVar3) {
        return 0xa0;
      }
      pbVar2 = pbVar2 + 2;
      if (*pbVar3 != 7) {
        return 0xa0;
      }
      bVar5 = 4;
    }
    else if (uVar7 == 0xd) {
      bVar5 = 2;
      pbVar2 = pbVar3;
    }
    else {
      if (uVar7 - 0xe < 2) {
        return 0xa0;
      }
      if (uVar7 - 0x15 < 2) {
        return 0xa0;
      }
      if (uVar7 - 0x1e < 2) {
        return 0xa0;
      }
      if (uVar7 - 0x1e == 0xe1) {
        if (pbVar1 < pbVar2 + 5) {
          return 0xa0;
        }
        uVar7 = (uint)pbVar2[4] |
                (uint)pbVar2[2] << 0x10 | (uint)*pbVar3 << 0x18 | (uint)pbVar2[3] << 8;
        if (64000 < uVar7 + 32000) {
          return 0xa0;
        }
        iVar6 = uVar7 << 0x10;
        pbVar2 = pbVar2 + 5;
      }
      else {
        if (*pbVar2 < 0x20) {
          return 0xa0;
        }
        if (*pbVar2 < 0xf7) {
          iVar6 = *pbVar2 - 0x8b;
        }
        else {
          pbVar3 = pbVar2 + 2;
          if (pbVar1 < pbVar3) {
            return 0xa0;
          }
          if (*pbVar2 < 0xfb) {
            iVar6 = DAT_005d2818 + (uint)*pbVar2 * 0x100 + (uint)pbVar2[1];
          }
          else {
            iVar6 = -(DAT_005d2814 + (uint)*pbVar2 * 0x100 + (uint)pbVar2[1]);
          }
        }
        iVar6 = iVar6 << 0x10;
        pbVar2 = pbVar3;
      }
    }
    if (bVar5 != 0) break;
    if (0xff < (int)piVar4 - (param_1 + 0x6c) >> 2) {
      return 0xa0;
    }
    *piVar4 = iVar6;
    *(int **)(param_1 + 0x46c) = piVar4 + 1;
  }
  iVar6 = *(int *)(DAT_005d281c + (uint)bVar5 * 4);
  if ((int)piVar4 - (param_1 + 0x6c) >> 2 < iVar6) {
    return 0xa1;
  }
  piVar4 = piVar4 + -iVar6;
  if (bVar5 != 2) {
    if (bVar5 != 4) {
      return 0xa0;
    }
    *(undefined1 *)(param_1 + 0x40) = 1;
    *(int *)(param_1 + 0x20) = *piVar4 + *(int *)(param_1 + 0x20);
    *(int *)(param_1 + 0x24) = piVar4[1] + *(int *)(param_1 + 0x24);
    *(int *)(param_1 + 0x28) = piVar4[2];
    *(int *)(param_1 + 0x2c) = piVar4[3];
    return 0;
  }
  *(undefined1 *)(param_1 + 0x40) = 1;
  *(int *)(param_1 + 0x20) = *piVar4 + *(int *)(param_1 + 0x20);
  *(int *)(param_1 + 0x28) = piVar4[1];
  *(undefined4 *)(param_1 + 0x2c) = 0;
  return 0;
}

