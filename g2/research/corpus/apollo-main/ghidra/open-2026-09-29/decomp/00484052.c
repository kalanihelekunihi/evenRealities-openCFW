
undefined8 FUN_00484052(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  int *piVar4;
  
  iVar1 = FUN_004645ec(0);
  bVar3 = 0;
  while (iVar2 = iVar1, iVar2 != 0) {
    iVar1 = FUN_004645ec(iVar2);
    if (((*(undefined1 **)(iVar2 + 8) == &LAB_004840ac_1) &&
        (piVar4 = *(int **)(iVar2 + 0xc), *piVar4 == param_1)) && (piVar4[1] == param_2)) {
      FUN_004644ee(iVar2);
      FUN_0044f758(piVar4);
      bVar3 = 1;
    }
  }
  return CONCAT44(param_4,(uint)bVar3);
}

