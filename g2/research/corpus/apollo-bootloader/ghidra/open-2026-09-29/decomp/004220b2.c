
undefined8 FUN_004220b2(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  char *pcVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint local_20;
  
  bVar2 = false;
  bVar3 = false;
  iVar8 = 0;
  iVar6 = FUN_004215dc(6,param_1);
  if (iVar6 == 0) {
    uVar7 = critical_save();
    iVar6 = FUN_004215fe(6);
    if (iVar6 == 0) {
      *DAT_0042245c = '\x01';
    }
    FUN_00421632(6,param_1,1);
    pcVar4 = DAT_00422438;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar7 & 1) == 1);
    }
    if (*DAT_00422438 != '\0') {
      if (*DAT_00422430 == '\0') {
        iVar8 = FUN_00421bd2(0x35);
        FUN_00421b08(0x35);
      }
      else {
        iVar8 = FUN_00421b08(0x35);
        FUN_00421bd2(0x35);
      }
    }
    local_20 = critical_save();
    if (iVar8 == 0) {
      if (*pcVar4 == '\0') {
        iVar8 = 1;
      }
      bVar3 = bVar2;
      if ((iVar8 == 0) && (*DAT_0042245c != '\0')) {
        *DAT_0042245c = '\0';
        piVar5 = DAT_00422460;
        if (*DAT_00422460 == 0) {
          iVar8 = bl_syspll_initialize(0,DAT_00422460);
        }
        if (iVar8 == 0) {
          iVar8 = syspll_configure_42740c(*piVar5,DAT_00422430);
        }
        if (iVar8 == 0) {
          iVar8 = syspll_enable_427360(*piVar5);
        }
        if (iVar8 == 0) {
          bVar3 = true;
        }
        else if (*piVar5 != 0) {
          syspll_deinitialize_427310(*piVar5);
          *piVar5 = 0;
        }
      }
      if (iVar8 != 0) {
        FUN_00421632(6,param_1,0);
      }
    }
    else {
      FUN_00421632(6,param_1,0);
    }
    bVar2 = (bool)isCurrentModePrivileged();
    if (bVar2) {
      enableIRQinterrupts((local_20 & 1) == 1);
    }
    if (*pcVar4 != '\0') {
      if (iVar8 == 0) {
        if (*DAT_00422430 == '\0') {
          FUN_00421b5c(0x35);
        }
        else {
          FUN_00421cce(0x35);
        }
      }
      else {
        FUN_00421cce(0x35);
        FUN_00421b5c(0x35);
      }
    }
    if (bVar3) {
      iVar8 = syspll_lock_wait_427522(*DAT_00422460);
    }
  }
  else {
    iVar8 = 0;
    local_20 = param_3;
  }
  return CONCAT44(local_20,iVar8);
}

