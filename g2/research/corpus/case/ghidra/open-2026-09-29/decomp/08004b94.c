
int case_copy_controller_words
              (uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined8 uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  pcVar1 = DAT_08004bec;
  if (*DAT_08004bec == '\x01') {
    iVar2 = 2;
  }
  else {
    *DAT_08004bec = '\x01';
    pcVar1[4] = '\0';
    pcVar1[5] = '\0';
    pcVar1[6] = '\0';
    pcVar1[7] = '\0';
    uVar4 = param_1;
    uVar5 = param_3;
    uVar3 = case_wait_serial_idle(1000);
    iVar2 = (int)uVar3;
    if (iVar2 == 0) {
      if (param_1 == 1) {
        case_register_pair_commit
                  (param_2,(int)((ulonglong)uVar3 >> 0x20),param_3,param_4,uVar4,param_2,uVar5);
      }
      else {
        case_copy64_protected(param_2,param_3);
      }
      iVar2 = case_wait_serial_idle(1000);
      *(uint *)(DAT_08004bf0 + 0x14) = *(uint *)(DAT_08004bf0 + 0x14) & ~param_1;
    }
    *pcVar1 = '\0';
  }
  return iVar2;
}

