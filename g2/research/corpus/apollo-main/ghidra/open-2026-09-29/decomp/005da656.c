
undefined8 FUN_005da656(uint param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  uint uVar4;
  int iVar5;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  local_14 = param_3;
  if (param_1 == 0) {
    *param_2 = 0x30;
    param_2 = param_2 + 1;
  }
  else {
    if ((int)param_1 < 0) {
      *param_2 = 0x2d;
      param_2 = param_2 + 1;
      param_1 = -param_1;
    }
    pbVar3 = (byte *)&local_14;
    for (uVar4 = param_1 >> 0x10; 0 < (int)uVar4; uVar4 = (int)uVar4 / 10) {
      *pbVar3 = (char)uVar4 + (char)((int)uVar4 / 10) * -10 + 0x30;
      pbVar3 = pbVar3 + 1;
    }
    while (&local_14 < pbVar3) {
      pbVar3 = pbVar3 + -1;
      *param_2 = *pbVar3;
      param_2 = param_2 + 1;
    }
    if ((param_1 & 0xffff) != 0) {
      *param_2 = 0x2e;
      pbVar3 = param_2 + 1;
      iVar1 = (param_1 & 0xffff) * 10 + 5;
      for (iVar5 = 0; iVar5 < 5; iVar5 = iVar5 + 1) {
        *pbVar3 = (char)(iVar1 / 0x10000) + 0x30;
        pbVar3 = pbVar3 + 1;
        iVar2 = iVar1 % 0x10000;
        iVar1 = 0;
        if (iVar2 == 0) break;
        iVar1 = iVar2 * 10;
      }
      pbVar3 = pbVar3 + -1;
      if ((int)pbVar3 - (int)param_2 == 5) {
        if ((iVar1 < DAT_005dae4c) && (*pbVar3 == 0x31)) {
          *pbVar3 = 0x30;
        }
        else if ((iVar1 == DAT_005dae50) && ((int)((uint)*pbVar3 << 0x1f) < 0)) {
          *pbVar3 = *pbVar3 - 1;
        }
        else if ((iVar1 < DAT_005dae50) && (*pbVar3 != 0x30)) {
          *pbVar3 = *pbVar3 - 1;
        }
      }
      for (; *pbVar3 == 0x30; pbVar3 = pbVar3 + -1) {
        *pbVar3 = 0;
      }
      param_2 = pbVar3 + 1;
    }
  }
  return CONCAT44(local_14,param_2);
}

