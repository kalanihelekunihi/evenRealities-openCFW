
uint touch_sub_3ec8(int *param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = *param_1;
  uVar1 = touch_sub_3084();
  *(undefined1 *)(param_1[7] + 0x15) = 0;
  *(undefined1 *)(param_1[2] + 0x52) = 0;
  *(undefined1 *)(param_1[2] + 0x74) = *(undefined1 *)(iVar5 + 0x29);
  *(undefined1 *)(param_1[2] + 0x75) = *(undefined1 *)(iVar5 + 0x2a);
  *(undefined1 *)(param_1[2] + 0x4c) = *(undefined1 *)(iVar5 + 0x2b);
  uVar2 = touch_config_2078_build(param_1);
  uVar1 = uVar1 | uVar2;
  touch_packet_23a4_build_group(0,param_1);
  touch_packet_23a4_build_group(1,param_1);
  *(undefined4 *)(param_1[2] + 0x10) = DAT_00007284;
  iVar5 = param_1[2];
  uVar3 = touch_sub_2a70(*(undefined4 *)(iVar5 + 0x24),param_1);
  *(undefined4 *)(iVar5 + 0x28) = uVar3;
  if (*(code **)(param_1[2] + 0x14) != (code *)0x0) {
    (**(code **)(param_1[2] + 0x14))(param_1);
  }
  if (uVar1 == 0) {
    uVar1 = event_dispatcher(1,param_1);
    if (uVar1 != 0) goto LAB_0000723c;
    uVar1 = event_dispatcher(2,param_1);
  }
  if (uVar1 == 0) {
    uVar1 = touch_sub_3d64(param_1);
  }
LAB_0000723c:
  for (uVar2 = 0; uVar2 < 3; uVar2 = uVar2 + 1) {
    iVar5 = touch_sub_4ade(uVar2,param_1);
    if (iVar5 != 0) {
      uVar4 = touch_sub_29ac(uVar2,param_1);
      uVar1 = uVar1 | uVar4;
    }
  }
  return uVar1;
}

