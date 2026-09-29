
undefined4 smpActCheckAttempts(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (*(char *)(param_1 + 0x42) != '\0') {
    *(undefined1 *)(param_1 + 0x42) = 0;
    smpSendPairingFailed(param_1,9);
    smpActNotifyDmAttemptsFailure(param_1,param_2);
    smpCleanup(param_1);
  }
  return param_4;
}

