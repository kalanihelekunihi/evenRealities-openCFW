
undefined8 gls_frame_pack_l(undefined4 param_1,int param_2,int param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  piVar1 = DAT_08008ffc;
  iVar4 = 1;
  iVar2 = param_2;
  iVar5 = param_3;
  do {
    disableIRQinterrupts();
    case_pulse4_train();
    iVar3 = FUN_08000420(0x5a,param_1,param_2,param_3,param_1,iVar2,iVar5);
    enableIRQinterrupts();
    if (iVar3 != 0) goto LAB_08008fc4;
    *piVar1 = *piVar1 + 1;
    if (piVar1[4] == 1) {
      g2_log_printf(DAT_08009000,piVar1[1],piVar1[2],piVar1[3]);
    }
    iVar4 = iVar4 + 1;
  } while (iVar4 != 10);
  for (iVar2 = 0; iVar2 < param_2; iVar2 = iVar2 + 1) {
    *(undefined1 *)(param_3 + iVar2) = 0xff;
  }
  iVar3 = 0;
LAB_08008fc4:
  return CONCAT44(param_1,iVar3);
}

