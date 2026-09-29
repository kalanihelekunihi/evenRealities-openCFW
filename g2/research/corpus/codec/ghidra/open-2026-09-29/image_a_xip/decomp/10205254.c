
int gx8002_aout_alloc_playback(uint param_1)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = iRam102052d8;
  if (((*(char *)(iRam102052d8 + 4) == '\0') && (*(int *)(iRam102052d8 + 8) == 0)) &&
     (*(byte *)(iRam102052d8 + 0xc) == param_1)) {
    gx8002_memset(iRam102052d8 + 0x10,0,0x24);
    *(undefined1 *)(iVar2 + 4) = 1;
  }
  else {
    iVar2 = 0;
  }
  *(undefined4 *)(iVar2 + 0x14) = 0;
  *(char *)(iVar2 + 0x18) = (char)param_1;
  piVar1 = (int *)gx8002_aout_select_hw_config();
  *(int **)(iVar2 + 0x30) = piVar1;
  uRam0000000c = uRam0000000c | 0x200000;
  uRam00000000 = piVar1[1] & 1U | *piVar1 * 2 & 2U | uRam00000000 & 0x3ffffffc;
  uRam00000004 = uRam00000004 & 0xfffffeff;
  func_0x1002553c(0xd,uRam102052dc,iVar2);
  return iVar2;
}

