
undefined1 FUN_00450500(int param_1,int param_2)

{
  bool bVar1;
  undefined4 uVar2;
  int *piVar3;
  undefined1 uVar4;
  
  uVar2 = DAT_00450b48;
  uVar4 = 0;
  piVar3 = (int *)FUN_00482cd8(DAT_00450b48);
  while (piVar3 != (int *)0x0) {
    bVar1 = false;
    if (((*piVar3 == param_1) || (param_1 == 0)) && ((piVar3[1] == param_2 || (param_2 == 0)))) {
      FUN_00450b0c(piVar3);
      FUN_004509da();
      uVar4 = 1;
      bVar1 = true;
    }
    if (bVar1) {
      piVar3 = (int *)FUN_00482cd8(uVar2);
    }
    else {
      piVar3 = (int *)FUN_00482cf0(uVar2,piVar3);
    }
  }
  return uVar4;
}

