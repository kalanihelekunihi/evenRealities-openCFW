
undefined1 productModeRead(void)

{
  int iVar1;
  
  iVar1 = DAT_004abea0;
  SVC_NvdbRead(DAT_004abeb8,DAT_004abea0,4);
  return *(undefined1 *)(iVar1 + 1);
}

