
void smpiScActJwncCalcG2(int param_1,int param_2)

{
  int iVar1;
  
  smpLogByteArray(PTR_s_Local_Cb_005e38b8,*(undefined4 *)(param_2 + 4),0x10);
  iVar1 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x40,*(undefined4 *)(param_2 + 4)
                       ,0x10);
  if (iVar1 == 0) {
    smpScActJwncCalcG2(param_1,param_2);
  }
  else {
    smpScFailWithReattempt(param_1);
  }
  return;
}

