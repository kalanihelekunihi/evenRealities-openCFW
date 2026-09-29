
undefined4 gx8002_spi_register_master(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  
  iVar1 = iRam10206160;
  if (param_1 == (int *)0x0) {
    uVar2 = 0xffffffed;
  }
  else {
    uVar3 = param_1[1];
    if ((uVar3 == 0) || (iVar5 = *param_1, iVar5 < 0)) {
      uVar2 = 0xffffffea;
    }
    else {
      piVar6 = *(int **)(iRam10206160 + 4);
      param_1[7] = iRam10206160;
      *(int **)(iVar1 + 4) = param_1 + 7;
      param_1[8] = (int)piVar6;
      *piVar6 = (int)(param_1 + 7);
      piVar6 = (int *)*(int *)(iVar1 + 8);
      do {
        piVar4 = piVar6;
        if (piVar4 == (int *)(iVar1 + 8)) goto LAB_1020614c;
        piVar6 = (int *)*piVar4;
      } while ((iVar5 != piVar4[-6]) || (uVar3 <= *(byte *)(piVar4 + -3)));
      piVar4[-5] = (int)param_1;
LAB_1020614c:
      uVar2 = 0;
    }
  }
  return uVar2;
}

