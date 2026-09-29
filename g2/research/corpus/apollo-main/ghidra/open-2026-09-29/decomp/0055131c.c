
undefined8 FUN_0055131c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  
  iVar4 = DAT_00551e9c;
  if (*(int *)(DAT_00551e9c + 0x3c) != 0) {
    iVar3 = FUN_0054ffb4(param_1);
    if ((iVar3 == 0) || (*(char *)(iVar3 + 10) == '\0')) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x5aa;
        param_3 = DAT_00551eb4;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551eb8,0x5aa,DAT_00551eb4,param_1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00551ebc,DAT_00551ebc,param_1);
      }
    }
    else {
      piVar5 = (int *)(iVar4 + (uint)*(byte *)(iVar3 + 9) * 0x28 + 0x40);
      if (*piVar5 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x5b1;
          param_3 = DAT_00551ec0;
          FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551eb8,0x5b1,DAT_00551ec0,
                       *(undefined1 *)(iVar3 + 9));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00551ec4,DAT_00551ec4,*(undefined1 *)(iVar3 + 9));
        }
      }
      else {
        *DAT_00551aa8 = *(undefined1 *)(iVar3 + 9);
        pcVar1 = DAT_00551aa4;
        cVar2 = service_ancc_message_count_get();
        *pcVar1 = cVar2;
        if (*pcVar1 < '\x04') {
          *DAT_00551ec8 = *pcVar1;
        }
        else {
          *DAT_00551ec8 = '\x03';
        }
        service_ancc_record_remove(param_1);
        FUN_00550c04(*piVar5,*(undefined1 *)(iVar3 + 8));
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

