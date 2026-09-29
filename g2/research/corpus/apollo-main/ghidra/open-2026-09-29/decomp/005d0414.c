
int FUN_005d0414(uint *param_1,uint param_2,int param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = 0;
  iVar3 = 0;
  uVar6 = 1;
  uVar2 = param_4 << 1;
  uVar4 = *param_1;
  if (uVar4 < param_2) {
    if (param_2 - uVar4 < uVar2) {
      uVar2 = param_2 - uVar4;
    }
    for (; uVar5 < uVar2; uVar5 = uVar5 + 1) {
      uVar1 = (uint)*(byte *)(uVar4 + uVar5);
      if (((((uVar1 != 0x20) && (uVar1 != 0xd)) && (uVar1 != 10)) &&
          ((uVar1 != 9 && (uVar1 != 0xc)))) && (uVar1 != 0)) {
        if ((0x7f < uVar1) || (uVar1 = (uint)*(char *)(DAT_005d070c + (uVar1 & 0x7f)), 0xf < uVar1))
        break;
        uVar6 = uVar1 | uVar6 << 4;
        if ((int)(uVar6 << 0x17) < 0) {
          *(char *)(param_3 + iVar3) = (char)uVar6;
          iVar3 = iVar3 + 1;
          uVar6 = 1;
        }
      }
    }
    if (uVar6 != 1) {
      *(char *)(param_3 + iVar3) = (char)(uVar6 << 4);
      iVar3 = iVar3 + 1;
    }
    *param_1 = uVar4 + uVar5;
  }
  else {
    iVar3 = 0;
  }
  return iVar3;
}

