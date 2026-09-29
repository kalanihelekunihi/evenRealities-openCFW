
uint touch_sub_3d64(int *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  uint local_24 [2];
  
  iVar4 = *param_1;
  uVar5 = **(undefined4 **)(iVar4 + 8);
  uVar1 = event_dispatcher(7,param_1);
  iVar7 = param_1[3];
  for (uVar6 = 0; uVar6 < 3; uVar6 = uVar6 + 1) {
    iVar2 = touch_sub_4ade(uVar6,param_1);
    if (((iVar2 != 0) && (*(char *)(iVar7 + 0x8a) == '\x02')) && (*(char *)(iVar7 + 0x7a) != '\n'))
    {
      if (*(char *)(iVar7 + 0x7b) == '\a') {
        uVar3 = msc_sensing_loop(param_1[0xb] + (uint)*(ushort *)(iVar7 + 0x80) * 0x2c + 0x14,iVar7,
                                 0xb,local_24,param_1);
      }
      else {
        uVar3 = msc_sensing_loop(param_1[10] + (uint)*(ushort *)(iVar7 + 0x80) * 0x1c,iVar7,7,
                                 local_24,param_1);
      }
      uVar1 = uVar1 | uVar3;
      if (local_24[0] < 0x21) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 6;
      }
      else if (local_24[0] < 0x38) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 5;
      }
      else if (local_24[0] < 0x70) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 4;
      }
      else if (local_24[0] < 0x152) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 3;
      }
      else if (local_24[0] < 0x234) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 2;
      }
      else if (local_24[0] < 0x468) {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 1;
      }
      else {
        *(undefined1 *)(param_1[4] + uVar6 * 0x3c + 0x33) = 0;
      }
    }
    iVar7 = iVar7 + 0x90;
  }
  touch_packet_23a4_build_group(0,param_1);
  touch_packet_23a4_build_group(1,param_1);
  iVar4 = Cy_MSCLP_Configure(uVar5,param_1[9],2,*(undefined4 *)(*(int *)(iVar4 + 8) + 4));
  if (iVar4 != 0) {
    uVar1 = 0x40;
  }
  return uVar1;
}

