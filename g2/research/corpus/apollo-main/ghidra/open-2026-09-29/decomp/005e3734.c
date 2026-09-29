
undefined4 smpiScActOobSendRand(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(char *)(param_1 + 0x22) == '\x01') {
    smpLogByteArray(PTR_s_Initiator_Cb_005e38bc,*(undefined4 *)(param_2 + 4),0x10);
    iVar1 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x40,
                         *(undefined4 *)(param_2 + 4),0x10);
    if (iVar1 != 0) {
      smpScFailWithReattempt(param_1);
      return param_4;
    }
  }
  *(undefined1 *)(param_1 + 0x3f) = 4;
  FUN_0053634e(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  smpLogByteArray(PTR_s_Rand_Na_005e38ac,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  smpScSendRand(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
  return param_4;
}

