
undefined4 FUN_000068ec(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *param_1;
  uVar2 = **(undefined4 **)(iVar1 + 8);
  touch_packet_23a4_build_group(0,param_1);
  touch_packet_23a4_build_group(1,param_1);
  iVar1 = Cy_MSCLP_Configure(uVar2,param_1[9],2,*(undefined4 *)(*(int *)(iVar1 + 8) + 4));
  touch_sub_355c(param_1);
  uVar2 = 0;
  if (iVar1 != 0) {
    uVar2 = 0x40;
  }
  return uVar2;
}

