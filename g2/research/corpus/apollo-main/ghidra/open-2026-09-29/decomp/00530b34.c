
undefined4 L2cInit(void)

{
  undefined4 *puVar1;
  undefined *puVar2;
  undefined4 unaff_r7;
  
  puVar2 = PTR_l2cDefaultDataCback_1_00530ba4;
  puVar1 = DAT_00530b90;
  *DAT_00530b90 = PTR_l2cDefaultDataCback_1_00530ba4;
  puVar1[1] = puVar2;
  puVar1[2] = PTR_l2cRxSignalingPkt_1_00530ba8;
  puVar2 = PTR_l2cDefaultCtrlCback_1_00530bac;
  puVar1[3] = PTR_l2cDefaultCtrlCback_1_00530bac;
  puVar1[4] = puVar2;
  puVar1[5] = puVar2;
  puVar1[8] = PTR_l2cDefaultDataCidCback_1_00530bb0;
  *(undefined1 *)(puVar1 + 9) = 1;
  func_0x005367f0(PTR_l2cHciAclCback_1_00530bb8,PTR_l2cHciFlowCback_1_00530bb4);
  return unaff_r7;
}

