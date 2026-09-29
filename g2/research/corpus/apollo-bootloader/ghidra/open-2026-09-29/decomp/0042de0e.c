
void critical_dispatch_transaction_42de0e(void)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 in_r3;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_10;
  
  local_1c = DAT_0042e178;
  local_20 = 0x1f9;
  uStack_10 = in_r3;
  elog_output(1,DAT_0042e118,DAT_0042e114,DAT_0042e17c);
  uVar2 = DAT_0042e180;
  uVar3 = critical_save();
  FUN_004156ac(&local_20,DAT_0042e184,0x10);
  alignment_dispatch_42e4f4(DAT_0042e188,&local_20,uVar2,4);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  terminal_mode_42e514(0,0);
  return;
}

