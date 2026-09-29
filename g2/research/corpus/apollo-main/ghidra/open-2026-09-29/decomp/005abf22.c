
short cff_cmap_encoding_char_next(int param_1,uint *param_2)

{
  short sVar1;
  uint uVar2;
  
  sVar1 = 0;
  uVar2 = *param_2;
  *param_2 = 0;
  if (uVar2 < 0xff) {
    do {
      uVar2 = uVar2 + 1;
      if (0xff < uVar2) {
        return 0;
      }
      sVar1 = *(short *)(*(int *)(param_1 + 0x10) + uVar2 * 2);
    } while (sVar1 == 0);
    *param_2 = uVar2;
  }
  return sVar1;
}

