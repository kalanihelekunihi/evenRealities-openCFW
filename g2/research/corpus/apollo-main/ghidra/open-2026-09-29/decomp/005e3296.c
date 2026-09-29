
undefined4 smpiActCnfVerify(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_004751c8(*(undefined4 *)(param_2 + 4),*(int *)(param_1 + 0x30) + 0x20,0x10);
  if (iVar1 == 0) {
    smpCalcS1(param_1,*(undefined4 *)(param_1 + 0x30),*(int *)(param_1 + 0x30) + 0x10,
              *(int *)(param_1 + 0x30) + 0x30);
  }
  else {
    *(undefined1 *)(param_2 + 3) = 4;
    *(char *)(param_1 + 0x42) = *(char *)(param_1 + 0x42) + '\x01';
    SmpDbPairingFailed(*(undefined1 *)(param_1 + 0x3d));
    if (*(char *)(param_1 + 0x42) == *(char *)(*DAT_005e3404 + 7)) {
      *(undefined1 *)(param_2 + 2) = 0xd;
    }
    else {
      *(undefined1 *)(param_2 + 2) = 3;
    }
    smpSmExecute(param_1,param_2);
  }
  return param_4;
}

