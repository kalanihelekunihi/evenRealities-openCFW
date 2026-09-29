
undefined8 FUN_0041be36(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  byte bVar2;
  uint *puVar3;
  uint *puVar4;
  int iVar5;
  undefined4 local_18;
  
  puVar3 = DAT_0041c834;
  local_18 = param_4;
  if ((uint)*param_1 != (*DAT_0041c834 & 7)) {
    bVar1 = (*DAT_0041c834 & 7) < (uint)*param_1;
    if (bVar1) {
      FUN_0041cd1a(6,1,param_1);
    }
    puVar4 = DAT_0041c864;
    *DAT_0041c864 = *param_1 & 7 | *DAT_0041c864 & 0xfffffff8;
    local_18 = 1;
    iVar5 = delay_us_status_check(5,DAT_0041c834,7,*puVar4);
    if (iVar5 != 0) goto LAB_0041bf38;
    if ((*puVar3 & 7) != (*puVar4 & 7)) {
      iVar5 = 1;
      goto LAB_0041bf38;
    }
    if (!bVar1) {
      FUN_0041cd1a(6,0,0);
    }
  }
  puVar3 = DAT_0041c868;
  *DAT_0041c868 = *DAT_0041c868 & 0xffffffc7 | (param_1[1] & 7) << 3;
  *puVar3 = *puVar3 & 0xfffff1ff | (param_1[2] & 7) << 9;
  *puVar3 = *puVar3 & 0xffff8fff | (param_1[3] & 7) << 0xc;
  bVar2 = param_1[4];
  if (bVar2 == 0) {
    *puVar3 = *puVar3 | 7;
  }
  else if (bVar2 == 1) {
    *puVar3 = *puVar3 & 0xfffffff8 | 6;
  }
  else if (bVar2 == 3) {
    *puVar3 = *puVar3 & 0xfffffff8 | 4;
  }
  else if (bVar2 == 7) {
    *puVar3 = *puVar3 & 0xfffffff8;
  }
  puVar3 = DAT_0041cae4;
  *DAT_0041cae4 = *DAT_0041cae4 & 0xffffc7ff;
  *puVar3 = *puVar3 & 0xfffff8ff;
  iVar5 = 0;
LAB_0041bf38:
  return CONCAT44(local_18,iVar5);
}

