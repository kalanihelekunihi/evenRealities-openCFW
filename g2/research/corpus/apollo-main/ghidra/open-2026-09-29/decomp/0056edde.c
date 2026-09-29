
undefined4 smpActNotifyDmAttemptsFailure(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_2 + 3) = 9;
  *(undefined1 *)(param_2 + 2) = 0x2b;
  DmSmpCbackExec();
  return unaff_r7;
}

