
undefined4 FUN_00466890(void)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  iVar2 = settings_get_terminal_mode();
  if (iVar2 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0x30;
  }
  FUN_00464b2e(uVar1,0,0,0);
  return unaff_r7;
}

