
undefined1 FUN_0055819e(byte *param_1,byte *param_2)

{
  undefined1 uVar1;
  int iVar2;
  byte bVar3;
  byte *pbVar4;
  byte *pbVar5;
  
  if (*param_1 == *param_2) {
    bVar3 = *param_1;
    if (bVar3 == 1) {
      if (((param_1[4] == param_2[4]) && (param_1[5] == param_2[5])) && (param_1[6] == param_2[6]))
      {
        uVar1 = 1;
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      if (bVar3 != 0) {
        if (bVar3 == 3) {
          if (((param_1[4] == param_2[4]) && (param_1[5] == param_2[5])) &&
             (param_1[6] == param_2[6])) {
            return 1;
          }
          return 0;
        }
        if (bVar3 < 3) {
          if (param_1[4] != param_2[4]) {
            return 0;
          }
          if (param_1[5] != param_2[5]) {
            return 0;
          }
          if (param_1[6] != param_2[6]) {
            return 0;
          }
          if (param_1[7] != param_2[7]) {
            return 0;
          }
          bVar3 = 0;
          while( true ) {
            if (param_1[7] <= bVar3) {
              return 1;
            }
            if ((param_1 + 4)[bVar3 + 4] != (param_2 + 4)[bVar3 + 4]) break;
            bVar3 = bVar3 + 1;
          }
          return 0;
        }
        if (bVar3 == 4) {
          pbVar4 = param_1 + 4;
          pbVar5 = param_2 + 4;
          if (*pbVar4 != *pbVar5) {
            return 0;
          }
          if (param_1[5] != param_2[5]) {
            return 0;
          }
          if (param_1[6] != param_2[6]) {
            return 0;
          }
          for (bVar3 = 0; bVar3 < param_1[6]; bVar3 = bVar3 + 1) {
            if (*(float *)(pbVar4 + (uint)bVar3 * 4 + 4) != *(float *)(pbVar5 + (uint)bVar3 * 4 + 4)
               ) {
              return 0;
            }
          }
          if (param_1[0x14] != param_2[0x14]) {
            return 0;
          }
          bVar3 = 0;
          while( true ) {
            if (param_1[0x14] <= bVar3) {
              return 1;
            }
            iVar2 = FUN_0044b610(pbVar4 + (uint)bVar3 * 0x20 + 0x11,
                                 pbVar5 + (uint)bVar3 * 0x20 + 0x11,0x20);
            if (iVar2 != 0) break;
            bVar3 = bVar3 + 1;
          }
          return 0;
        }
      }
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

