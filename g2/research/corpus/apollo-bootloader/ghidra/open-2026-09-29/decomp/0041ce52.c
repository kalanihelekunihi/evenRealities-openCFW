
undefined4 FUN_0041ce52(void)

{
  int *piVar1;
  uint *puVar2;
  uint *puVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_0041d11c;
  uVar4 = 0;
  FUN_0041560c(DAT_0041d11c,0x3c,0);
  puVar2 = DAT_0041d120;
  if ((((*DAT_0041d120 & 0xff) == 0x23) && (1 < *DAT_0041d124)) || (0x23 < (*DAT_0041d120 & 0xff)))
  {
    *DAT_0041d128 = '\x01';
  }
  else {
    *DAT_0041d128 = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_0041d124 == 2)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_0041d124 == 1)))) {
    *DAT_0041d12c = '\x01';
  }
  else {
    *DAT_0041d12c = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x21) && (*DAT_0041d124 == 2)) ||
     ((((*puVar2 & 0xff) == 0x21 && (*DAT_0041d124 == 3)) ||
      (((*puVar2 & 0xff) == 0x22 && (*DAT_0041d124 == 0)))))) {
    *DAT_0041d130 = '\x01';
  }
  else {
    *DAT_0041d130 = '\0';
  }
  if (((*puVar2 & 0xff) == 0x21) && (2 < *DAT_0041d124)) {
    *DAT_0041d134 = 1;
  }
  else {
    *DAT_0041d134 = 0;
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_0041d124 == 1)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_0041d124 == 0)))) {
    *DAT_0041d138 = '\x01';
  }
  else {
    *DAT_0041d138 = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_0041d124 == 2)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_0041d124 == 1)))) {
    *DAT_0041d140 = *(byte *)(DAT_0041d13c + 0x34) & 1 ^ 1;
  }
  else {
    *DAT_0041d140 = 0;
  }
  puVar3 = DAT_0041d144;
  if ((*DAT_0041d130 != '\0' || *DAT_0041d138 != '\0') || *DAT_0041d140 != 0) {
    *DAT_0041d144 = *DAT_0041d144 & 0xfffffffd;
    *puVar3 = *puVar3 | 1;
    puVar3 = DAT_0041d148;
    *DAT_0041d148 = *DAT_0041d148 | 0x8000;
    *puVar3 = *puVar3 | 0x4000;
    *puVar3 = *puVar3 | 0x2000;
  }
  if (*DAT_0041d128 == '\0') {
    if (*DAT_0041d12c == '\0') {
      if (((((*puVar2 & 0xff) == 0x21) && (1 < *DAT_0041d124)) ||
          (((*puVar2 & 0xff) == 0x22 && (*DAT_0041d124 < 2)))) ||
         (((*puVar2 & 0xff) == 0x23 && (*DAT_0041d124 == 0)))) {
        *piVar1 = DAT_0041d180;
        piVar1[1] = DAT_0041d184;
        piVar1[2] = DAT_0041d188;
        piVar1[3] = DAT_0041d18c;
        piVar1[4] = DAT_0041d190;
        piVar1[0xc] = DAT_0041d194;
        piVar1[0xd] = DAT_0041d198;
        piVar1[0xe] = DAT_0041d19c;
        if (((*puVar2 & 0xff) == 0x21) && (*DAT_0041d124 == 2)) {
          piVar1[6] = DAT_0041d1a0;
          piVar1[7] = DAT_0041d1a4;
        }
        else {
          piVar1[6] = DAT_0041d1a8;
          piVar1[7] = DAT_0041d1ac;
        }
      }
      else if (((*puVar2 & 0xff) == 0x21) && (*DAT_0041d124 == 1)) {
        *piVar1 = DAT_0041d1b0;
        piVar1[1] = DAT_0041d1b4;
        piVar1[6] = DAT_0041d1a0;
        piVar1[7] = DAT_0041d1a4;
      }
    }
    else {
      *piVar1 = DAT_0041d164;
      piVar1[1] = DAT_0041d168;
      piVar1[2] = DAT_0041d16c;
      piVar1[5] = DAT_0041d170;
      piVar1[6] = DAT_0041d174;
      piVar1[7] = DAT_0041d178;
      piVar1[0xb] = DAT_0041d17c;
    }
  }
  else {
    *piVar1 = DAT_0041d14c;
    piVar1[1] = DAT_0041d150;
    piVar1[2] = DAT_0041d154;
    piVar1[7] = DAT_0041d158;
    piVar1[10] = DAT_0041d15c;
    piVar1[0xb] = DAT_0041d160;
  }
  if (((*puVar2 & 0xff) == 0x21) && (*DAT_0041d124 < 2)) {
    piVar1[8] = DAT_0041d1b8;
    piVar1[9] = DAT_0041d1bc;
  }
  if (*piVar1 != 0) {
    uVar4 = (*(code *)*piVar1)();
  }
  return uVar4;
}

