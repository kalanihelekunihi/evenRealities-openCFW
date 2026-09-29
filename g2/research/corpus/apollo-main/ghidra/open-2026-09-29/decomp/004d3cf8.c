
int FUN_004d3cf8(uint param_1,int param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  
  iVar2 = 0;
  if (((param_2 - 1U < 0xc) && (-1 < (int)param_1)) && (0 < (int)param_3)) {
    if (*(uint *)(DAT_004d3dc4 + param_2 * 4 + -4) < param_3) {
      if ((((param_2 == 2) && ((param_1 & 3) == 0)) &&
          (((int)param_1 % 100 != 0 || ((int)param_1 % 400 != 0)))) && (param_3 == 0x1d)) {
        bVar1 = false;
      }
      else {
        bVar1 = true;
      }
    }
    else {
      bVar1 = false;
    }
    if (bVar1) {
      iVar2 = 7;
    }
    else {
      if ((((param_1 & 3) == 0) && (((int)param_1 % 100 != 0 || ((int)param_1 % 400 != 0)))) &&
         (param_2 < 3)) {
        iVar2 = -1;
      }
      iVar2 = (int)(iVar2 + *(int *)(DAT_004d3dc8 + param_2 * 4 + -4) +
                            (int)param_1 / 400 +
                            (((int)param_1 / 4 + param_1 + 2) - (int)param_1 / 100) + param_3) % 7;
    }
  }
  else {
    iVar2 = 7;
  }
  return iVar2;
}

