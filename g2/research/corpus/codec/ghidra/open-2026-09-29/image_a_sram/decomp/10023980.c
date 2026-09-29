
undefined4 gx8002_flash_write_protect_mode(void)

{
  undefined4 uVar1;
  int *piVar2;
  
  piVar2 = *(int **)(*(int *)(DAT_100239a0 + 0xc) + 0x10);
  if (piVar2 == (int *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = 0xffffffff;
    if (*piVar2 != 0) {
      uVar1 = 1;
    }
  }
  return uVar1;
}

