
void FUN_100060e8(uint param_1)

{
  uint *puVar1;
  int iVar2;
  
  if (0 < *DAT_10006128) {
    iVar2 = 0;
    puVar1 = DAT_1000612c;
    do {
      if ((*puVar1 <= param_1) && (param_1 <= *puVar1 + puVar1[1])) {
        FUN_10007240(*(undefined4 *)(DAT_10006130 + iVar2 * 0xc),param_1);
        return;
      }
      iVar2 = iVar2 + 1;
      puVar1 = puVar1 + 3;
    } while (iVar2 != *DAT_10006128);
  }
  return;
}

