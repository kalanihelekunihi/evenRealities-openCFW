
undefined4 gx8002_padmux_init(char *param_1,int param_2)

{
  char cVar1;
  char cVar2;
  int iVar3;
  char *pcVar4;
  undefined4 uVar5;
  char *pcVar6;
  int iVar7;
  int iVar8;
  
  iVar3 = iRam1020667c;
  if ((param_1 == (char *)0x0) || (param_2 < 0)) {
    uVar5 = 0xffffffff;
  }
  else {
    iVar8 = 1;
    do {
      iVar7 = iVar8 * 2 + iVar3;
      cVar1 = *(char *)(iVar7 + -2);
      pcVar4 = param_1;
      do {
        pcVar6 = pcVar4;
        if (param_1 + param_2 * 2 == pcVar6) {
          cVar2 = *(char *)(iVar7 + -1);
          goto LAB_10206666;
        }
        pcVar4 = pcVar6 + 2;
      } while (cVar1 != *pcVar6);
      cVar2 = pcVar6[1];
LAB_10206666:
      iVar8 = iVar8 + 1;
      gx8002_padmux_set(cVar1,cVar2);
    } while (iVar8 != 0x21);
    uVar5 = 0;
  }
  return uVar5;
}

