
int FUN_005dadf8(int param_1,int param_2)

{
  int *piVar1;
  
  piVar1 = DAT_005db934;
  while( true ) {
    if (DAT_005db934 + 0x21 <= piVar1) {
      return 0;
    }
    if ((*piVar1 == param_1) && ((piVar1[1] == param_2 || (piVar1[1] == -1)))) break;
    piVar1 = piVar1 + 3;
  }
  return piVar1[2];
}

