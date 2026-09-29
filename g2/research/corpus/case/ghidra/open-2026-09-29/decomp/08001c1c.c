
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void glasses_status_force_refresh(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  undefined1 uVar4;
  undefined1 local_20 [3];
  undefined1 uStack_1d;
  byte local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  
  pcVar2 = _DAT_08001d10;
  iVar1 = DAT_08001d0c;
  if (param_1 != 0 || param_2 != 0) {
    _local_20 = DAT_08001d04;
    if (*(char *)(DAT_08001d0c + 4) == '\0') {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
    uStack_1a = (undefined2)((uint)DAT_08001d08 >> 0x10);
    _local_1c = CONCAT11(uVar4,*(char *)(DAT_08001d0c + 3) << 7 | *(byte *)(DAT_08001d0c + 1));
    uStack_18 = param_4;
    if ((param_1 != 0) && (*(char *)(DAT_08001d0c + 0x10) != '\0')) {
      uStack_1d = (undefined1)((uint)DAT_08001d04 >> 0x18);
      local_20._0_2_ = (undefined2)DAT_08001d04;
      local_20 = (undefined1  [3])CONCAT12(0,local_20._0_2_);
      case_finalize_length_checksum(local_20,7);
      gls_uart_transfer_controlled(1,local_20,7);
      *(int *)(iVar1 + 0x48) = *(int *)(iVar1 + 0x48) + 1;
      iVar3 = gls_frame_validate_dispatch(1);
      if (iVar3 == 0x13) {
        *(undefined4 *)(iVar1 + 0x40) = 0;
        *(undefined4 *)(iVar1 + 0x44) = 0;
        *(int *)(iVar1 + 0x3c) = *(int *)(iVar1 + 0x3c) + 1;
      }
      else {
        *(undefined4 *)(iVar1 + 0x3c) = 0;
        *(int *)(iVar1 + 0x40) = *(int *)(iVar1 + 0x40) + 1;
        if (*pcVar2 == '\0') {
          g2_log_printf(s_Fail_to_get_GLS_L_status_FORCE___08001d13 + 1);
          g2_log_printf(&DAT_08001d3c);
        }
      }
    }
    if ((param_2 != 0) && (*(char *)(iVar1 + 0x11) != '\0')) {
      local_20 = (undefined1  [3])CONCAT12(1,local_20._0_2_);
      case_finalize_length_checksum(local_20,7);
      gls_uart_transfer_controlled(0,local_20,7,1);
      *(int *)(iVar1 + 100) = *(int *)(iVar1 + 100) + 1;
      iVar3 = gls_frame_validate_dispatch(0);
      if (iVar3 == 0x13) {
        *(undefined4 *)(iVar1 + 0x5c) = 0;
        *(undefined4 *)(iVar1 + 0x60) = 0;
        *(int *)(iVar1 + 0x58) = *(int *)(iVar1 + 0x58) + 1;
        return;
      }
      *(undefined4 *)(iVar1 + 0x58) = 0;
      *(int *)(iVar1 + 0x5c) = *(int *)(iVar1 + 0x5c) + 1;
      if (*pcVar2 == '\0') {
        g2_log_printf(s_Fail_to_get_GLS_R_status_FORCE___08001d40);
        g2_log_printf(&DAT_08001d3c);
      }
    }
  }
  return;
}

