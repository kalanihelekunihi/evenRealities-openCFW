
undefined4
smpL2cCtrlCback(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = smpCcbByConnId((char)*param_1);
  if ((*(char *)(iVar1 + 0x3d) != '\0') &&
     (*(bool *)(iVar1 + 0x3c) = *(char *)(param_1 + 1) == '\x01', *(char *)(iVar1 + 0x3c) == '\0'))
  {
    if (*(int *)(iVar1 + 0x34) != 0) {
      uVar3 = *(undefined4 *)(iVar1 + 0x34);
      *(undefined4 *)(iVar1 + 0x34) = 0;
      smpSendPkt(iVar1,uVar3);
    }
    iVar2 = smpStateIdle(iVar1);
    if (iVar2 == 0) {
      *(undefined1 *)(param_1 + 1) = 0xc;
      smpSmExecute(iVar1,param_1);
    }
  }
  return param_4;
}

