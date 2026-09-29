
undefined4 FT_Select_Charmap(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  
  if (param_1 == 0) {
    uVar1 = 0x23;
  }
  else if (param_2 == 0) {
    uVar1 = 6;
  }
  else if (param_2 == DAT_005273b4) {
    uVar1 = find_unicode_charmap();
  }
  else {
    piVar2 = *(int **)(param_1 + 0x28);
    if (piVar2 == (int *)0x0) {
      uVar1 = 0x26;
    }
    else {
      piVar3 = piVar2 + *(int *)(param_1 + 0x24);
      for (; piVar2 < piVar3; piVar2 = piVar2 + 1) {
        if (*(int *)(*piVar2 + 4) == param_2) {
          *(int *)(param_1 + 0x5c) = *piVar2;
          return 0;
        }
      }
      uVar1 = 6;
    }
  }
  return uVar1;
}

