
uint touch_sub_4280(int param_1,undefined4 param_2,uint param_3,byte *param_4,int param_5)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  bool bVar8;
  uint local_30;
  
  iVar5 = *(int *)(param_5 + 0xc) + param_1 * 0x90;
  bVar7 = -1 < (int)((uint)*(ushort *)(iVar5 + 0x8e) << 0x1c);
  bVar8 = *(char *)(iVar5 + 0x7a) != '\x01';
  uVar2 = touch_sub_2c6a(param_1,param_2,param_5);
  *param_4 = 0;
  bVar1 = 0;
  local_30 = DAT_00007678;
  uVar6 = 0;
  for (; param_3 != 0; param_3 = param_3 >> 1) {
    *param_4 = *param_4 | (byte)param_3;
    touch_sub_2b64(param_1,param_5);
    uVar3 = touch_sub_422e(param_1,param_5);
    uVar6 = uVar6 | uVar3;
    touch_state_2902_cap_enabled_object(param_1,param_5);
    uVar3 = touch_sub_2c34(param_1,param_2,param_5);
    if ((bVar7) && (uVar4 = touch_sub_2c5e(uVar3,uVar2), uVar4 < local_30)) {
      bVar1 = *param_4;
      local_30 = uVar4;
    }
    if (((!bVar8) && (uVar3 < uVar2)) || ((bVar8 && (uVar2 <= uVar3)))) {
      *param_4 = *param_4 & ~(byte)param_3;
    }
  }
  if (bVar7) {
    *param_4 = bVar1;
  }
  return uVar6;
}

