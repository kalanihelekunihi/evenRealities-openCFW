
bool retained_state_probe_42e224(void)

{
  undefined4 in_r3;
  int iVar1;
  
  iVar1 = *DAT_0042e458;
  elog_output(3,DAT_0042e468,DAT_0042e464,DAT_0042e460,0x40,DAT_0042e45c,iVar1,in_r3);
  return iVar1 == 0x55555555;
}

