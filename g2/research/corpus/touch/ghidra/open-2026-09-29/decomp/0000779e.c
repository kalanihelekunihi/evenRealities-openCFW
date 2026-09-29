
uint touch_sub_449e(int param_1,int *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar1 = touch_sub_422e();
  touch_state_2902_cap_enabled_object(param_1,param_2);
  if (*(char *)(param_2[3] + param_1 * 0x90 + 0x7a) == '\x01') {
    uVar5 = (uint)*(byte *)(*param_2 + 0x30);
    uVar6 = (uint)*(byte *)(param_2[2] + 0x57);
  }
  else {
    uVar5 = 0;
    uVar6 = 0;
    uVar1 = 1;
  }
  uVar2 = touch_sub_2c34(param_1,0,param_2);
  if (uVar5 < uVar6) {
    iVar3 = uVar6 - uVar5;
  }
  else {
    iVar3 = 0;
  }
  uVar5 = uVar5 + uVar6;
  if (100 < uVar5) {
    uVar5 = 100;
  }
  uVar4 = (uint)*(ushort *)(param_2[4] + param_1 * 0x3c + 4);
  uVar6 = __aeabi_uidiv(uVar4 * iVar3,100);
  if ((uVar2 < uVar6) || (uVar6 = __aeabi_uidiv(uVar4 * uVar5,100), uVar6 < uVar2)) {
    uVar1 = uVar1 | 0x200;
  }
  return uVar1;
}

