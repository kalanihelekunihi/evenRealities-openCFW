
undefined4 smprScActPkSendRand(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  smpLogByteArray(&DAT_005e420c,*(undefined4 *)(param_2 + 4),0x10);
  smpLogByteArray(PTR_s_Ca_Peer_005e421c,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,0x10);
  iVar1 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,*(undefined4 *)(param_2 + 4)
                       ,0x10);
  if (iVar1 == 0) {
    *(char *)(*(int *)(param_1 + 0x48) + 3) = *(char *)(*(int *)(param_1 + 0x48) + 3) + '\x01';
    if (*(byte *)(*(int *)(param_1 + 0x48) + 3) < 0x14) {
      *(undefined1 *)(param_1 + 0x3f) = 3;
      uStack_10._0_3_ = CONCAT12(0x1a,(undefined2)uStack_10);
      smpScSendRand(param_1,param_2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
    }
    else {
      uStack_10 = CONCAT13(uStack_10._3_1_,0x1b0000);
    }
    uStack_10 = CONCAT22(uStack_10._2_2_,(ushort)*(byte *)(param_1 + 0x3d));
    smpSmExecute(param_1,&uStack_10);
  }
  else {
    smpScFailWithReattempt(param_1);
  }
  return uStack_10;
}

