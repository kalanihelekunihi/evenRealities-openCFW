
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void HciDrvHandlerInit(undefined1 param_1)

{
  int iVar1;
  
  *DAT_004b4da4 = param_1;
  iVar1 = DAT_004b4d9c;
  *(undefined1 *)(DAT_004b4d9c + 0xc) = param_1;
  *(undefined1 *)(iVar1 + 10) = 2;
  iVar1 = _DAT_004b4da8;
  *(undefined1 *)(_DAT_004b4da8 + 0xc) = param_1;
  *(undefined1 *)(iVar1 + 10) = 3;
  return;
}

