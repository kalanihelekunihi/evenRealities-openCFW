
void FUN_0048eb32(undefined4 param_1,uint param_2,int param_3)

{
  if (8 < param_2) {
    param_2 = 8;
  }
  if (param_3 == 0) {
    param_2 = 0;
  }
  if (*DAT_0048ed88 == '\0') {
    FUN_0048eac8();
  }
  FUN_0048ea66(param_1,param_2,param_3);
  if (((0xbff < (uint)(*(int *)(DAT_0048ed78 + 8) - *(int *)(DAT_0048ed78 + 0x10))) &&
      (*DAT_0048ed94 == '\0')) && (*DAT_0048ed98 == '\0')) {
    *DAT_0048ed94 = '\x01';
    FUN_0047dd92();
  }
  return;
}

