
undefined4 FUN_00532124(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  
  iVar1 = DAT_00532638 + (uint)*param_1 * 0x10;
  piVar2 = (int *)(iVar1 + -0x10);
  *(undefined1 *)(iVar1 + -5) = 0;
  DmConnSetIdle((char)*(undefined2 *)param_1,8,0);
  iVar1 = FUN_004bb07c((char)*(undefined2 *)param_1);
  if (iVar1 != 0) {
    FUN_0047b488(iVar1,0);
  }
  if (*piVar2 != 0) {
    WsfBufFree(*piVar2);
    *piVar2 = 0;
  }
  return param_4;
}

