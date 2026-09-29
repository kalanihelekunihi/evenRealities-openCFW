
void case_pulse4_train_pre_delay(void)

{
  undefined4 extraout_r1;
  undefined4 uVar1;
  undefined4 extraout_r1_00;
  uint uVar2;
  int extraout_r2;
  
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_busy_delay(0x15e);
  case_write_mask4_clear();
  uVar2 = 0;
  uVar1 = extraout_r1;
  do {
    case_busy_delay(0x15e,uVar1,uVar2);
    uVar2 = extraout_r2 + 1U & 0xff;
    uVar1 = extraout_r1_00;
  } while (uVar2 < 0x28);
  case_write_mask4_set();
  return;
}

