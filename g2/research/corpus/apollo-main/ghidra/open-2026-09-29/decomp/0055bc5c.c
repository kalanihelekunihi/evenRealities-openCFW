
undefined4 dmConnSmActCancelOpen(void)

{
  undefined4 unaff_r7;
  
  HciLeCreateConnCancelCmd();
  dmDevPassEvtToDevPriv(0xe,1,0,0);
  return unaff_r7;
}

