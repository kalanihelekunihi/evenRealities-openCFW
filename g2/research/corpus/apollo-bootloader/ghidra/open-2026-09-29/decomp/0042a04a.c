
uint spotmgr_timer_irq_service_42a04a(void)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save();
  if (*DAT_0042abb4 == '\x02') {
    spotmgr_transition_sequence_2b_428378();
  }
  else if (*DAT_0042abb4 == '\a') {
    spotmgr_transition_sequence_7b_428a94();
  }
  FUN_0041ccd6();
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar2;
}

