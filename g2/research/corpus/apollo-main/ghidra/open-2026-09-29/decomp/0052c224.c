
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void AttsCccRegister(undefined1 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = DAT_0052c674;
  *(undefined1 *)(DAT_0052c674 + 0x14) = param_1;
  *(undefined4 *)(iVar1 + 0xc) = param_2;
  *(undefined4 *)(iVar1 + 0x10) = param_3;
  *(undefined4 *)(_DAT_0052c6a8 + 0x26c) = _DAT_0052c6a4;
  return;
}

