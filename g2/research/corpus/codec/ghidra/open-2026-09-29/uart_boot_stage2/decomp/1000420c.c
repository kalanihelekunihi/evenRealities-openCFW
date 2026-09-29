
void FUN_1000420c(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = FUN_10003110();
  iVar1 = DAT_1000424c;
  *(undefined1 *)(param_1 + DAT_1000424c + 0x370) = 0;
  if ((*(uint *)(iVar1 + 4) == 0) ||
     ((*(char *)(iVar1 + 0x370) != '\x01' &&
      ((*(uint *)(iVar1 + 4) < 2 || (*(char *)(iVar1 + 0x371) != '\x01')))))) {
    FUN_10004a48(0x19,0);
  }
  FUN_1000311c(uVar2);
  return;
}

