
undefined4 smprScActOobSendRand(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(char *)(param_1 + 0x29) == '\x01') {
    smpLogByteArray(&DAT_005e420c,*(undefined4 *)(param_2 + 4),0x10);
    iVar1 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,
                         *(undefined4 *)(param_2 + 4),0x10);
    if (iVar1 != 0) {
      smpScFailWithReattempt(param_1);
      return param_4;
    }
  }
  *(undefined1 *)(param_1 + 0x3f) = 0xd;
  FUN_0053634e(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
  smpLogByteArray(PTR_s_Rand_Nb_005e4214,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
  smpScSendRand(param_1,param_2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
  return param_4;
}

