
void crc32_no_comp(undefined4 param_1,uint param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = param_3;
  if ((param_2 & 3) != 0) {
    while (uVar3 != 0) {
      param_2 = param_2 + 1;
      param_3 = param_3 - 1;
      if (param_3 == 0) break;
      uVar3 = param_2 & 3;
    }
  }
  for (uVar3 = 0; param_3 >> 2 != uVar3; uVar3 = uVar3 + 1) {
  }
  if ((param_3 & 3) != 0) {
    iVar1 = param_2 + (param_3 >> 2) * 4 + -1;
    iVar2 = iVar1 + (param_3 & 3);
    do {
      iVar1 = iVar1 + 1;
    } while (iVar1 != iVar2);
  }
  return;
}

