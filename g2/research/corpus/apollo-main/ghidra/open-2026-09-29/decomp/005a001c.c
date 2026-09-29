
void FUN_005a001c(byte param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = 0;
  if ((*DAT_005a09c4 != '\0') && ((*DAT_005a09c8 & 0x3f) >> 4 == 3)) {
    if ((*DAT_005a09cc << 0xd < 0) && (*DAT_005a09d0 != '\0')) {
      bVar1 = true;
    }
    else {
      bVar1 = false;
    }
    if (bVar1) {
      iVar3 = 0xf;
    }
    if (param_1 == 0) {
      iVar2 = 10;
    }
    else if (param_1 == 2) {
      iVar2 = 0;
    }
    else if (param_1 < 2) {
      iVar2 = 10;
    }
    else {
      iVar2 = 0;
    }
    if (iVar2 - iVar3 < 1) {
      if ((iVar3 - iVar2) + *DAT_005a09d4 < 0x80) {
        uVar4 = (iVar3 - iVar2) + *DAT_005a09d4;
      }
      else {
        uVar4 = 0x7f;
      }
      *DAT_005a09d8 = *DAT_005a09d8 & 0xffffff80 | uVar4 & 0x7f;
    }
    else {
      if ((uint)(iVar2 - iVar3) < *DAT_005a09d4) {
        uVar4 = *DAT_005a09d4 - (iVar2 - iVar3);
      }
      else {
        uVar4 = 0;
      }
      *DAT_005a09d8 = *DAT_005a09d8 & 0xffffff80 | uVar4 & 0x7f;
    }
  }
  return;
}

