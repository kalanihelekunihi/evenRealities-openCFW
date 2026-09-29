
int FUN_005cf99a(uint *param_1)

{
  int iVar1;
  byte *pbVar2;
  uint uVar3;
  
  FUN_005cf8e4(param_1);
  if ((int)param_1[3] < 2) {
    iVar1 = *param_1 - 1;
    do {
      if (*param_1 < param_1[2]) {
        pbVar2 = (byte *)*param_1;
        *param_1 = (uint)(pbVar2 + 1);
        uVar3 = (uint)*pbVar2;
      }
      else {
        uVar3 = 0xffffffff;
      }
      if ((uVar3 == 0xd) || (uVar3 == 10)) {
        param_1[3] = 2;
        return iVar1;
      }
    } while ((uVar3 != 0xffffffff) && (uVar3 != 0x1a));
    param_1[3] = 3;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

