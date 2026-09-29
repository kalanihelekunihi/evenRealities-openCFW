
undefined8 FT_Get_Font_Format(int param_1)

{
  undefined4 uVar1;
  int *piVar2;
  undefined4 unaff_r7;
  
  uVar1 = 0;
  if (param_1 != 0) {
    piVar2 = *(int **)(param_1 + 0x60);
    uVar1 = 0;
    if (*(int *)(*piVar2 + 0x20) != 0) {
      uVar1 = (**(code **)(*piVar2 + 0x20))(piVar2,DAT_00524f14);
    }
  }
  return CONCAT44(unaff_r7,uVar1);
}

