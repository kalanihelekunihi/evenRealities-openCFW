
uint spotmgr_trim_commit_42ae9c(void)

{
  bool bVar1;
  char *pcVar2;
  uint *puVar3;
  uint uVar4;
  
  uVar4 = critical_save();
  spotmgr_trim_restore_42ae6c();
  puVar3 = DAT_0042b9d0;
  pcVar2 = DAT_0042b9c8;
  if (*DAT_0042b9c8 != '\0') {
    if ((*DAT_0042b9cc != 8) && (*DAT_0042b9cc != 0xc)) {
      *DAT_0042b9d0 = *DAT_0042b9d0 | 8;
      *puVar3 = *puVar3 | 0x40;
    }
    *pcVar2 = '\0';
  }
  FUN_0041ccd6();
  spotmgr_profile_trim_42ae24(1);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar4 & 1) == 1);
  }
  return uVar4;
}

