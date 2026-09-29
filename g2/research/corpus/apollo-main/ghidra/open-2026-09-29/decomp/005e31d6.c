
uint smpiActProcPairRsp(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  
  iVar2 = *(int *)(param_2 + 4);
  uStack_18 = param_4;
  FUN_00439be4(param_1 + 0x27,iVar2 + 8,7);
  iVar1 = DAT_005e3408;
  if (((*(byte *)(iVar2 + 0xd) & ~*(byte *)(param_1 + 0x25)) == 0) &&
     ((*(byte *)(iVar2 + 0xe) & ~*(byte *)(param_1 + 0x26)) == 0)) {
    iVar2 = (**(code **)(DAT_005e3408 + 0xf0))(param_1,(int)&uStack_18 + 1,&uStack_18);
    if (iVar2 != 0) {
      (**(code **)(iVar1 + 0xf4))(param_1,uStack_18._1_1_,uStack_18 & 0xff);
    }
  }
  else {
    *(undefined1 *)(param_2 + 3) = 10;
    *(undefined1 *)(param_2 + 2) = 3;
    smpSmExecute(param_1,param_2);
  }
  return uStack_18;
}

