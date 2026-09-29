
int * FUN_00450566(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  
  uVar1 = DAT_00450b48;
  piVar2 = (int *)FUN_00482cd8(DAT_00450b48);
  do {
    if (piVar2 == (int *)0x0) {
      return (int *)0x0;
    }
    if (*piVar2 == param_1) {
      if (piVar2[1] == param_2) {
        return piVar2;
      }
      if (param_2 == 0) {
        return piVar2;
      }
    }
    piVar2 = (int *)FUN_00482cf0(uVar1);
  } while( true );
}

