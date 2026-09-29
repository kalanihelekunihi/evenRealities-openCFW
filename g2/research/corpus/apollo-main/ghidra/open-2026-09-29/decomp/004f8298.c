
void FUN_004f8298(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004f8fbc;
  if (*DAT_004f8fbc != 0) {
    if ((*(int *)*DAT_004f8fbc == 0) ||
       (iVar2 = FUN_0043e2ea(*(undefined4 *)*DAT_004f8fbc), iVar2 == 0)) {
      FUN_00463e1c(*piVar1,0);
    }
    else {
      FUN_00463e1c(*piVar1,1);
    }
    *piVar1 = 0;
  }
  return;
}

