
int FUN_08004a6c(uint *param_1)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  pcVar1 = DAT_08004b18;
  if (*DAT_08004b18 == '\x01') {
    return 2;
  }
  *DAT_08004b18 = '\x01';
  pcVar1[4] = '\0';
  iVar2 = DAT_08004b1c;
  pcVar1[5] = '\0';
  pcVar1[6] = '\0';
  pcVar1[7] = '\0';
  if ((*param_1 & 1) != 0) {
    uVar6 = param_1[1];
    uVar5 = param_1[2];
    uVar3 = param_1[3];
    if (uVar6 == 1) {
      *(uint *)(DAT_08004b1c + 0x2c) = uVar3 << 0x10 | uVar5;
    }
    else if (uVar6 == 4) {
      *(uint *)(DAT_08004b1c + 0x4c) = uVar3 << 0x10 | uVar5;
    }
    else if (uVar6 == 8) {
      *(uint *)(DAT_08004b1c + 0x50) = uVar3 << 0x10 | uVar5;
    }
    else {
      *(uint *)(DAT_08004b1c + 0x30) = uVar3 << 0x10 | uVar5;
    }
  }
  uVar3 = *param_1;
  if ((uVar3 & 7) >> 1 == 3) {
    uVar3 = param_1[4];
LAB_08004ae6:
    uVar5 = param_1[6];
    uVar6 = param_1[5];
  }
  else {
    if (-1 < (int)(uVar3 << 0x1e)) {
      if (-1 < (int)(uVar3 << 0x1d)) goto LAB_08004aee;
      uVar3 = case_flash_status_classify();
      goto LAB_08004ae6;
    }
    uVar6 = case_flash_status_masked();
    uVar3 = param_1[4];
    uVar5 = uVar6;
  }
  case_flash_control_update(uVar6,uVar5,uVar3);
LAB_08004aee:
  iVar4 = case_wait_serial_idle(1000);
  if (iVar4 == 0) {
    *(uint *)(iVar2 + 0x14) = *(uint *)(iVar2 + 0x14) | 0x20000;
    iVar4 = case_wait_serial_idle(1000);
    *(uint *)(iVar2 + 0x14) = *(uint *)(iVar2 + 0x14) & 0xfffdffff;
  }
  *pcVar1 = '\0';
  return iVar4;
}

