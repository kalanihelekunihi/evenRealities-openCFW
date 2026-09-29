
undefined4 gx8002_spi_register_master(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  
  iVar1 = iRam10008278;
  if (param_1 == (int *)0x0) {
    uVar2 = 0xffffffed;
  }
  else {
    uVar6 = param_1[1];
    if ((uVar6 == 0) || (iVar5 = *param_1, iVar5 < 0)) {
      uVar2 = 0xffffffea;
    }
    else {
      piVar3 = *(int **)(iRam10008278 + 4);
      param_1[7] = iRam10008278;
      *(int **)(iVar1 + 4) = param_1 + 7;
      param_1[8] = (int)piVar3;
      *piVar3 = (int)(param_1 + 7);
      piVar3 = (int *)*(int *)(iVar1 + 8);
      do {
        piVar4 = piVar3;
        if (piVar4 == (int *)(iVar1 + 8)) {
          return 0;
        }
        piVar3 = (int *)*piVar4;
      } while ((iVar5 != piVar4[-6]) || (uVar6 <= *(byte *)(piVar4 + -3)));
      piVar4[-5] = (int)param_1;
      uVar2 = 0;
    }
  }
  return uVar2;
}

