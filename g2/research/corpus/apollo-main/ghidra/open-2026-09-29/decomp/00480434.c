
undefined4 FUN_00480434(void)

{
  int *piVar1;
  uint *puVar2;
  uint *puVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_004806fc;
  uVar4 = 0;
  FUN_0043c0e4(DAT_004806fc,0x3c,0);
  puVar2 = DAT_00480700;
  if ((((*DAT_00480700 & 0xff) == 0x23) && (1 < *DAT_00480704)) || (0x23 < (*DAT_00480700 & 0xff)))
  {
    *DAT_00480708 = '\x01';
  }
  else {
    *DAT_00480708 = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_00480704 == 2)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_00480704 == 1)))) {
    *DAT_0048070c = '\x01';
  }
  else {
    *DAT_0048070c = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x21) && (*DAT_00480704 == 2)) ||
     ((((*puVar2 & 0xff) == 0x21 && (*DAT_00480704 == 3)) ||
      (((*puVar2 & 0xff) == 0x22 && (*DAT_00480704 == 0)))))) {
    *DAT_00480710 = '\x01';
  }
  else {
    *DAT_00480710 = '\0';
  }
  if (((*puVar2 & 0xff) == 0x21) && (2 < *DAT_00480704)) {
    *DAT_00480714 = 1;
  }
  else {
    *DAT_00480714 = 0;
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_00480704 == 1)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_00480704 == 0)))) {
    *DAT_00480718 = '\x01';
  }
  else {
    *DAT_00480718 = '\0';
  }
  if ((((*puVar2 & 0xff) == 0x22) && (*DAT_00480704 == 2)) ||
     (((*puVar2 & 0xff) == 0x23 && (*DAT_00480704 == 1)))) {
    *DAT_00480720 = *(byte *)(DAT_0048071c + 0x34) & 1 ^ 1;
  }
  else {
    *DAT_00480720 = 0;
  }
  puVar3 = DAT_00480724;
  if ((*DAT_00480710 != '\0' || *DAT_00480718 != '\0') || *DAT_00480720 != 0) {
    *DAT_00480724 = *DAT_00480724 & 0xfffffffd;
    *puVar3 = *puVar3 | 1;
    puVar3 = DAT_00480728;
    *DAT_00480728 = *DAT_00480728 | 0x8000;
    *puVar3 = *puVar3 | 0x4000;
    *puVar3 = *puVar3 | 0x2000;
  }
  if (*DAT_00480708 == '\0') {
    if (*DAT_0048070c == '\0') {
      if (((((*puVar2 & 0xff) == 0x21) && (1 < *DAT_00480704)) ||
          (((*puVar2 & 0xff) == 0x22 && (*DAT_00480704 < 2)))) ||
         (((*puVar2 & 0xff) == 0x23 && (*DAT_00480704 == 0)))) {
        *piVar1 = DAT_00480760;
        piVar1[1] = DAT_00480764;
        piVar1[2] = DAT_00480768;
        piVar1[3] = DAT_0048076c;
        piVar1[4] = DAT_00480770;
        piVar1[0xc] = DAT_00480774;
        piVar1[0xd] = DAT_00480778;
        piVar1[0xe] = DAT_0048077c;
        if (((*puVar2 & 0xff) == 0x21) && (*DAT_00480704 == 2)) {
          piVar1[6] = DAT_00480780;
          piVar1[7] = DAT_00480784;
        }
        else {
          piVar1[6] = DAT_00480788;
          piVar1[7] = DAT_0048078c;
        }
      }
      else if (((*puVar2 & 0xff) == 0x21) && (*DAT_00480704 == 1)) {
        *piVar1 = DAT_00480790;
        piVar1[1] = DAT_00480794;
        piVar1[6] = DAT_00480780;
        piVar1[7] = DAT_00480784;
      }
    }
    else {
      *piVar1 = DAT_00480744;
      piVar1[1] = DAT_00480748;
      piVar1[2] = DAT_0048074c;
      piVar1[5] = DAT_00480750;
      piVar1[6] = DAT_00480754;
      piVar1[7] = DAT_00480758;
      piVar1[0xb] = DAT_0048075c;
    }
  }
  else {
    *piVar1 = DAT_0048072c;
    piVar1[1] = DAT_00480730;
    piVar1[2] = DAT_00480734;
    piVar1[7] = DAT_00480738;
    piVar1[10] = DAT_0048073c;
    piVar1[0xb] = DAT_00480740;
  }
  if (((*puVar2 & 0xff) == 0x21) && (*DAT_00480704 < 2)) {
    piVar1[8] = DAT_00480798;
    piVar1[9] = DAT_0048079c;
  }
  if (*piVar1 != 0) {
    uVar4 = (*(code *)*piVar1)();
  }
  return uVar4;
}

