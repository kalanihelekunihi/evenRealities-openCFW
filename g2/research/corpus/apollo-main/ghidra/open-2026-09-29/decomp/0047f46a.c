
undefined8 FUN_0047f46a(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  byte bVar2;
  uint *puVar3;
  uint *puVar4;
  int iVar5;
  undefined4 local_18;
  
  puVar3 = DAT_0047fe68;
  local_18 = param_4;
  if ((uint)*param_1 != (*DAT_0047fe68 & 7)) {
    bVar1 = (*DAT_0047fe68 & 7) < (uint)*param_1;
    if (bVar1) {
      FUN_00480312(6,1,param_1);
    }
    puVar4 = DAT_0047fe98;
    *DAT_0047fe98 = *param_1 & 7 | *DAT_0047fe98 & 0xfffffff8;
    local_18 = 1;
    iVar5 = FUN_00480826(5,DAT_0047fe68,7,*puVar4);
    if (iVar5 != 0) goto LAB_0047f56c;
    if ((*puVar3 & 7) != (*puVar4 & 7)) {
      iVar5 = 1;
      goto LAB_0047f56c;
    }
    if (!bVar1) {
      FUN_00480312(6,0,0);
    }
  }
  puVar3 = DAT_0047fe9c;
  *DAT_0047fe9c = *DAT_0047fe9c & 0xffffffc7 | (param_1[1] & 7) << 3;
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
  puVar3 = DAT_004800e0;
  *DAT_004800e0 = *DAT_004800e0 & 0xffffc7ff;
  *puVar3 = *puVar3 & 0xfffff8ff;
  iVar5 = 0;
LAB_0047f56c:
  return CONCAT44(local_18,iVar5);
}

