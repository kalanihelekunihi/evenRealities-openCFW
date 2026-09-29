
void FUN_00556ad4(void)

{
  int iVar1;
  
  iVar1 = DAT_005573fc;
  if (((*(int *)(DAT_005573fc + 0x14) != 0) && (*(int *)(DAT_005573fc + 0x40) == 0)) &&
     (*(char *)(DAT_005573fc + 0x44) == '\0')) {
    FUN_00556a28(1,0);
    *(undefined1 *)(iVar1 + 0x44) = 1;
  }
  return;
}

