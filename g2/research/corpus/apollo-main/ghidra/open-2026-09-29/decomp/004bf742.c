
void profileAnccInit(undefined1 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int *piVar2;
  
  iVar1 = DAT_004bf970;
  *(undefined1 *)(DAT_004bf970 + 1) = param_1;
  FUN_0043c0e4(iVar1 + 0x1c,0x300,0);
  FUN_0043c0e4(DAT_004bf900,0x2fc,0);
  piVar2 = DAT_004bf974;
  *DAT_004bf974 = param_2;
  *DAT_004bf978 = param_3;
  *DAT_004bf8f0 = *piVar2 + 0x30;
  _anccResetStateMachine();
  return;
}

