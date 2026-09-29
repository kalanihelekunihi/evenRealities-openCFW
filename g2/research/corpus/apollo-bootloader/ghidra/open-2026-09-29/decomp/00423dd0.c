
undefined8 stage_two_status(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = critical_save();
  pcVar2 = DAT_00423e10;
  if (*DAT_00423e10 != '\0') {
    *DAT_00423e10 = *DAT_00423e10 + -1;
  }
  if (*pcVar2 == '\0') {
    *DAT_00423e0c = 0;
    iVar4 = debug_disable();
    if (iVar4 == 3) {
      iVar4 = 0;
    }
  }
  else {
    iVar4 = 3;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(uVar3,iVar4);
}

