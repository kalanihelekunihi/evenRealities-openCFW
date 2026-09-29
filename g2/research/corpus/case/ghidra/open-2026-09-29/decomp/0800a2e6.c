
void case_pulse4_train(void)

{
  undefined4 extraout_r1;
  undefined4 uVar1;
  undefined4 extraout_r1_00;
  int iVar2;
  int extraout_r2;
  undefined4 uVar3;
  undefined4 extraout_r3;
  
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_write_mask4_clear();
  iVar2 = 0;
  uVar3 = 0x15e;
  uVar1 = extraout_r1;
  do {
    case_busy_delay(uVar3,uVar1,iVar2);
    iVar2 = extraout_r2 + 1;
    uVar3 = extraout_r3;
    uVar1 = extraout_r1_00;
  } while (iVar2 < 0x28);
  case_write_mask4_set();
  return;
}

