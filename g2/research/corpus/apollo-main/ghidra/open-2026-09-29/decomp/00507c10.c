
undefined4 FUN_00507c10(int param_1,int param_2,undefined1 *param_3)

{
  byte bVar1;
  byte *pbVar2;
  
  pbVar2 = (byte *)(param_2 + 5);
  if (-1 < (int)((uint)*pbVar2 << 0x1f)) {
    if (-1 < (char)*pbVar2) {
      *param_3 = 3;
      return 0;
    }
    *param_3 = 7;
    return 0;
  }
  if ((char)*pbVar2 < '\0') {
    bVar1 = *(byte *)(param_1 + 0x12) & 3;
    if (bVar1 == 1) {
      *param_3 = 6;
      return 0;
    }
    if ((*(byte *)(param_1 + 0x12) & 3) != 0) {
      if (bVar1 == 3) {
        *param_3 = 4;
        return 0;
      }
      if (bVar1 < 3) {
        *param_3 = 5;
        return 0;
      }
    }
    return 0xffffffff;
  }
  bVar1 = *(byte *)(param_1 + 0x12) & 3;
  if (bVar1 == 1) {
    *param_3 = 1;
    return 0;
  }
  if ((*(byte *)(param_1 + 0x12) & 3) != 0) {
    if (bVar1 == 3) {
      *param_3 = 2;
      return 0;
    }
    if (bVar1 < 3) {
      *param_3 = 0;
      return 0;
    }
  }
  return 0xffffffff;
}

