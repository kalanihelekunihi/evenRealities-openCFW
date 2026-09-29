
undefined4 FUN_005398e0(int param_1,int *param_2)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_00539da4;
  if (param_1 == 0) {
    if (param_2 == (int *)0x0) {
      uVar2 = 6;
    }
    else if ((int)(*DAT_00539da4 << 7) < 0) {
      uVar2 = 7;
    }
    else {
      *DAT_00539da4 = *DAT_00539da4 | 0x1000000;
      *puVar1 = *puVar1 & 0xff000000 | DAT_00539da8;
      puVar1[1] = 0;
      FUN_00480058();
      *param_2 = (int)puVar1;
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}

