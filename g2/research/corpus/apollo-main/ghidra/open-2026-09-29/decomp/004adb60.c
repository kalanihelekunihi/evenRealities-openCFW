
uint als_function_10(void)

{
  uint uVar1;
  uint uVar2;
  
  if (*DAT_004ae4cc < 5) {
    uVar1 = *(uint *)(DAT_004ae3b8 + *DAT_004ae3b4 * 4);
  }
  else {
    uVar1 = 0;
    for (uVar2 = 0; uVar2 < 5; uVar2 = uVar2 + 1) {
      if (uVar1 <= *(uint *)(DAT_004ae3b8 + uVar2 * 4)) {
        uVar1 = *(uint *)(DAT_004ae3b8 + uVar2 * 4);
      }
    }
  }
  return uVar1;
}

