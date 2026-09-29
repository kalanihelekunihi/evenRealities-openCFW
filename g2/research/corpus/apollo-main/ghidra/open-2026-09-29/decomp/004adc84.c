
bool als_function_12(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  bool bVar4;
  
  if (*DAT_004ae4cc < 5) {
    bVar4 = false;
  }
  else {
    uVar1 = *DAT_004ae3b8;
    uVar2 = *DAT_004ae3b8;
    for (uVar3 = 1; uVar3 < 5; uVar3 = uVar3 + 1) {
      if (uVar1 <= DAT_004ae3b8[uVar3]) {
        uVar1 = DAT_004ae3b8[uVar3];
      }
      if (DAT_004ae3b8[uVar3] <= uVar2) {
        uVar2 = DAT_004ae3b8[uVar3];
      }
    }
    bVar4 = 300 < uVar1 - uVar2;
  }
  return bVar4;
}

