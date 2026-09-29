
undefined4 AttHandlerInit(undefined1 param_1)

{
  int iVar1;
  undefined *puVar2;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004b51d0;
  *(undefined1 *)(DAT_004b51d0 + 0x60) = param_1;
  puVar2 = PTR_PTR_004b51ec;
  *(undefined **)(iVar1 + 0x3c) = PTR_PTR_004b51ec;
  *(undefined **)(iVar1 + 0x40) = puVar2;
  puVar2 = PTR_PTR_004b51f0;
  *(undefined **)(iVar1 + 0x44) = PTR_PTR_004b51f0;
  *(undefined **)(iVar1 + 0x48) = puVar2;
  L2cRegister(4,PTR_attL2cDataCback_1_004b51f8,PTR_attL2cCtrlCback_1_004b51f4);
  DmConnRegister(0,PTR_attDmConnCback_1_004b51fc);
  return unaff_r7;
}

