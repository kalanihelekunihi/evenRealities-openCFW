
undefined4 FUN_005320c2(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_00532638 + (uint)*param_1 * 0x10;
  *(undefined1 *)(iVar1 + -4) = 0;
  *(undefined1 *)(iVar1 + -8) = 0;
  *(undefined1 *)(iVar1 + -7) = 0;
  *(undefined1 *)(iVar1 + -3) = 0;
  *(undefined1 *)(iVar1 + -2) = 0;
  *(undefined1 *)(iVar1 + -5) = 0;
  (*(code *)*DAT_0053290c)((char)*(undefined2 *)param_1,0);
  if (*(int *)(iVar1 + -0xc) != 0) {
    FUN_0043c0e4(*(undefined4 *)(iVar1 + -0xc),(uint)*(byte *)(iVar1 + -6) << 1,0);
  }
  if (*(char *)*DAT_0053291c == '\0') {
    FUN_00531d60((char)*(undefined2 *)param_1);
  }
  return param_4;
}

