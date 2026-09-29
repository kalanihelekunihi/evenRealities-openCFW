
undefined8 gls_frame_pack_r(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_0800903c;
  iVar3 = 1;
  uVar4 = param_2;
  uVar5 = param_3;
  do {
    disableIRQinterrupts();
    case_pulse4_train();
    iVar2 = FUN_0800056c(0x5a,param_1,param_2,param_3,param_1,uVar4,uVar5);
    enableIRQinterrupts();
    if (iVar2 != 0) goto LAB_08009012;
    iVar3 = iVar3 + 1;
    *piVar1 = *piVar1 + 1;
  } while (iVar3 != 10);
  iVar2 = 0;
LAB_08009012:
  return CONCAT44(param_1,iVar2);
}

