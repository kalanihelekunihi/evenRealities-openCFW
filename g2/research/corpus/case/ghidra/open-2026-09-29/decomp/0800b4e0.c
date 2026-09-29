
undefined4 case_probe_low_signal(uint *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = DAT_0800b534;
  *(undefined4 *)(DAT_0800b534 + 8) = 0;
  iVar5 = 0;
  *(undefined4 *)(iVar1 + 0xc) = 0;
  case_transition_word8();
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_write_mask4_clear();
  case_transition_word4();
  case_busy_delay(0x17);
  uVar3 = case_read_mask4();
  *param_1 = ~uVar3 & 1;
  iVar2 = DAT_0800b538;
  do {
    iVar5 = iVar5 + 1;
    if (iVar2 < iVar5) {
      *(undefined4 *)(iVar1 + 0xc) = 1;
      return 0;
    }
    iVar4 = case_read_mask4();
  } while (iVar4 == 0);
  return 1;
}

