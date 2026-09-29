
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool FUN_08001408(void)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  bool bVar5;
  undefined4 local_24;
  undefined4 local_20;
  undefined1 local_1c [3];
  undefined1 uStack_19;
  byte local_18;
  undefined1 uStack_17;
  undefined2 uStack_16;
  
  pcVar1 = _DAT_08001514;
  iVar3 = DAT_0800150c;
  if ((*(char *)(DAT_0800150c + 0x10) == '\0') || (*(char *)(DAT_0800150c + 0x11) == '\0')) {
    if (*DAT_08001510 == '\0') {
      g2_log_printf(s_GetAgingStatus_fail__not_inbox_08001517 + 1);
      g2_log_printf(&DAT_08001538);
    }
    bVar5 = false;
  }
  else if (*_DAT_08001514 == '\0') {
    *_DAT_08001514 = '\x01';
    local_20 = DAT_08001568;
    local_24 = DAT_08001564;
    case_finalize_length_checksum(&local_24,5);
    gls_uart_transfer_controlled(1,&local_24,5);
    iVar2 = gls_frame_validate_dispatch(1);
    if (*(char *)(iVar3 + 4) == '\0') {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
    uStack_16 = (undefined2)((uint)DAT_08001570 >> 0x10);
    _local_18 = CONCAT11(uVar4,*(char *)(iVar3 + 3) << 7 | *(byte *)(iVar3 + 1));
    uStack_19 = (undefined1)((uint)DAT_0800156c >> 0x18);
    local_1c._0_2_ = (undefined2)DAT_0800156c;
    local_1c = (undefined1  [3])CONCAT12(0,local_1c._0_2_);
    case_finalize_length_checksum(local_1c,7);
    gls_uart_transfer_controlled(1,local_1c,7);
    gls_frame_validate_dispatch(1);
    local_1c = (undefined1  [3])CONCAT12(1,local_1c._0_2_);
    case_finalize_length_checksum(local_1c,7);
    gls_uart_transfer_controlled(0,local_1c,7,1);
    gls_frame_validate_dispatch(0);
    local_24._0_3_ = CONCAT12(1,(undefined2)local_24);
    case_finalize_length_checksum(&local_24,5);
    gls_uart_transfer_controlled(0,&local_24,5,1);
    iVar3 = gls_frame_validate_dispatch(0);
    bVar5 = iVar3 == 0x46 && iVar2 == 0x46;
    *pcVar1 = '\0';
  }
  else {
    if (*DAT_08001510 == '\0') {
      g2_log_printf(s_Skip_GetAgingStatus_since_2510_b_0800153c);
      g2_log_printf(&DAT_08001538);
    }
    bVar5 = true;
  }
  return bVar5;
}

