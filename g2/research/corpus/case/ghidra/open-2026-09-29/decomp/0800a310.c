
void case_pulse8_double_train(void)

{
  undefined4 extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 uVar1;
  undefined4 extraout_r1_02;
  int iVar2;
  int extraout_r2;
  int extraout_r2_00;
  
  case_write_mask8_set();
  case_transition_word4_alt();
  case_write_mask8_set();
  case_write_mask8_clear();
  iVar2 = 0;
  uVar1 = extraout_r1;
  do {
    case_busy_delay_alt(0x15e,uVar1,iVar2);
    iVar2 = extraout_r2 + 1;
    uVar1 = extraout_r1_00;
  } while (iVar2 < 10);
  case_write_mask8_set();
  case_busy_delay_alt(0x17);
  case_write_mask8_clear();
  iVar2 = 0;
  uVar1 = extraout_r1_01;
  do {
    case_busy_delay_alt(0x15e,uVar1,iVar2);
    iVar2 = extraout_r2_00 + 1;
    uVar1 = extraout_r1_02;
  } while (iVar2 < 10);
  case_write_mask8_set();
  return;
}

