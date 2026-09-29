
bool als_function_07(void)

{
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  uVar1 = 0;
  if (*DAT_004ae3c4 < 0x14) {
    bVar3 = false;
  }
  else {
    for (uVar2 = 0; uVar2 < 0x14; uVar2 = uVar2 + 1) {
      if (*(uint *)(DAT_004ae3c0 + uVar2 * 4) < 3) {
        uVar1 = uVar1 + 1;
      }
    }
    bVar3 = 0x12 < uVar1;
  }
  return bVar3;
}

