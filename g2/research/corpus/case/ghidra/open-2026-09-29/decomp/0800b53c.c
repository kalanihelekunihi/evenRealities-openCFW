
ulonglong case_probe_high_signal(uint *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  
  iVar1 = DAT_0800b5a4;
  *(undefined4 *)(DAT_0800b5a4 + 0xc) = 0;
  uVar7 = 1;
  iVar6 = 0;
  *(undefined4 *)(iVar1 + 0x10) = 0;
  case_transition_word4_alt();
  case_transition_word8_alt();
  iVar2 = DAT_0800b5a8;
  do {
    iVar6 = iVar6 + 1;
    if (iVar2 < iVar6) {
      uVar7 = 0;
      *(undefined4 *)(iVar1 + 0xc) = 1;
      break;
    }
    iVar5 = case_read_mask8();
  } while (iVar5 == 1);
  case_busy_delay_alt(0x32);
  uVar3 = case_read_mask8();
  uVar4 = ~uVar3 & 1;
  iVar6 = 0;
  *param_1 = uVar4;
  do {
    iVar6 = iVar6 + 1;
    if (iVar2 < iVar6) {
      uVar7 = 0;
      *(undefined4 *)(iVar1 + 0x10) = 1;
      break;
    }
    iVar5 = case_read_mask8();
  } while (iVar5 == 0);
  *param_1 = uVar4;
  return CONCAT44(~uVar3,uVar7) & 0x1ffffffff;
}

