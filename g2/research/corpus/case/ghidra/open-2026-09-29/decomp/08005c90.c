
void FUN_08005c90(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) * 0x40000000)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1e))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffd;
    *(undefined1 *)(param_1 + 7) = 1;
    if ((*(uint *)(*param_1 + 0x18) & 3) == 0) {
      case_hook_08005e14(param_1);
      case_hook_08005e16(param_1);
    }
    else {
      case_hook_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1d)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1d))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffb;
    *(undefined1 *)(param_1 + 7) = 2;
    if ((*(uint *)(*param_1 + 0x18) & 0x3ff) >> 8 == 0) {
      case_hook_08005e14(param_1);
      case_hook_08005e16(param_1);
    }
    else {
      case_hook_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1c)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1c))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffff7;
    *(undefined1 *)(param_1 + 7) = 4;
    if ((*(uint *)(*param_1 + 0x1c) & 3) == 0) {
      case_hook_08005e14(param_1);
      case_hook_08005e16(param_1);
    }
    else {
      case_hook_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1b)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1b))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffef;
    *(undefined1 *)(param_1 + 7) = 8;
    if ((*(uint *)(*param_1 + 0x1c) & 0x3ff) >> 8 == 0) {
      case_hook_08005e14(param_1);
      case_hook_08005e16(param_1);
    }
    else {
      case_hook_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if (((~*(uint *)(iVar1 + 0x10) & 1) == 0) && ((~*(uint *)(iVar1 + 0xc) & 1) == 0)) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffe;
    case_run_if_token(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x18)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x18))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffff7f;
    case_hook_08005bd6(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x17)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x18))) {
    *(undefined4 *)(iVar1 + 0x10) = DAT_08005e10;
    case_hook_08005bd4(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x19)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x19))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffbf;
    case_hook_08005e2c(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1a)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1a))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffdf;
    case_hook_08005bd8(param_1);
  }
  return;
}

