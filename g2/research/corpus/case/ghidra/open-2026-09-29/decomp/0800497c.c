
int case_run_controller_range(int *param_1,uint *param_2)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  
  pcVar1 = DAT_080049f8;
  if (*DAT_080049f8 == '\x01') {
    return 2;
  }
  *DAT_080049f8 = '\x01';
  pcVar1[4] = '\0';
  pcVar1[5] = '\0';
  pcVar1[6] = '\0';
  pcVar1[7] = '\0';
  iVar2 = case_wait_serial_idle(1000);
  if (iVar2 == 0) {
    if (*param_1 == 4) {
      case_control_word5_set(param_1[1]);
      iVar2 = case_wait_serial_idle(1000);
    }
    else {
      *param_2 = 0xffffffff;
      for (uVar3 = param_1[2]; uVar3 < (uint)(param_1[2] + param_1[3]); uVar3 = uVar3 + 1) {
        case_gpio_policy_update(param_1[1],uVar3);
        iVar2 = case_wait_serial_idle(1000);
        if (iVar2 != 0) {
          *param_2 = uVar3;
          break;
        }
      }
      *(uint *)(DAT_080049fc + 0x14) = *(uint *)(DAT_080049fc + 0x14) & 0xfffffffd;
    }
  }
  *pcVar1 = '\0';
  return iVar2;
}

