
int touch_sub_48c0(uint *param_1,int param_2,int param_3,undefined4 param_4,int *param_5)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint *puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  uint local_34;
  undefined4 local_30;
  uint local_2c;
  
  iVar8 = param_5[3] + param_2 * 0x90;
  iVar9 = param_5[4];
  puVar4 = (uint *)**(int **)(*param_5 + 8);
  iVar2 = event_dispatcher(5,param_5);
  iVar5 = param_5[10] + param_3 * 0x1c;
  if (*(char *)(iVar8 + 0x7b) == '\a') {
    iVar5 = param_5[0xb] + param_3 * 0x2c + 0x14;
  }
  local_40 = 0;
  local_3c = 0;
  local_38 = 0;
  local_30 = *(undefined4 *)(iVar5 + 0x10);
  local_2c = *(uint *)(iVar5 + 0x14);
  local_34 = *(uint *)(iVar5 + 0xc) & DAT_00007cf0;
  if (iVar2 == 0) {
    msclp_scan_register_prepare(&local_40,param_5);
    uVar3 = touch_sub_3f88(param_2,param_3,param_5);
    iVar5 = msclp_scan_start_wait(uVar3,param_5);
    if (iVar5 == 0) {
      iVar2 = 4;
    }
  }
  uVar6 = puVar4[0xc80];
  *puVar4 = *puVar4 & 0x7fffffff;
  *param_1 = DAT_00007cf4;
  uVar7 = local_2c >> 0x10 & 0xfff;
  bVar1 = *(byte *)(iVar9 + param_2 * 0x3c + 0x21) & 3;
  if (bVar1 == 2) {
    iVar5 = 0x60;
  }
  else {
    iVar5 = 2;
  }
  iVar5 = iVar5 * (uVar7 + 4 >> 2);
  if (((bVar1 == 2) && ((*(char *)(iVar8 + 0x7a) == '\x01' || (*(char *)(iVar8 + 0x7a) == '\n'))))
     || (-1 < (int)((uVar7 + 1) * -0x80000000))) {
    iVar5 = iVar5 + -1;
  }
  uVar6 = (uint)*(byte *)(iVar8 + 0x84) * ((uVar6 & 0xffff) - iVar5);
  if (uVar6 < 0x10000) {
    *param_1 = uVar6 & 0xffff;
  }
  if (*param_1 == 0) {
    *param_1 = 1;
  }
  return iVar2;
}

