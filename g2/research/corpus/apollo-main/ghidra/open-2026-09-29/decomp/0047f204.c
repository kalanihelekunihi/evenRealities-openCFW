
undefined8 FUN_0047f204(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  bool bVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  undefined4 local_28;
  uint local_24;
  undefined4 uStack_20;
  
  local_24 = 0;
  uVar8 = 0;
  bVar2 = false;
  *DAT_0047fad0 = *param_1;
  if (*param_1 == '\0') {
    uVar8 = 0x20;
    local_24 = 0x80;
  }
  uVar8 = uVar8 | (byte)param_1[1] & 7;
  local_24 = local_24 | (byte)param_1[1] & 7;
  cVar1 = param_1[3];
  if (cVar1 != '\0') {
    if (cVar1 == '\x01') {
      uVar8 = uVar8 | 8;
      local_24 = local_24 | 8;
    }
    else if (cVar1 == '\x03') {
      uVar8 = uVar8 | 0x18;
      local_24 = local_24 | 0x48;
    }
  }
  if ((param_1[3] == '\x03') && ((*DAT_0047fad4 & 0x48) == 8)) {
    *DAT_0047fad8 = *DAT_0047fad8 | 1;
    bVar2 = true;
  }
  puVar5 = DAT_0047fadc;
  puVar3 = DAT_0047fad4;
  local_28 = param_2;
  if (local_24 != *DAT_0047fad4) {
    uVar6 = *DAT_0047fad4;
    *DAT_0047fadc = *DAT_0047fadc & uVar8;
    puVar4 = DAT_0047fad4;
    local_28 = 1;
    uStack_20 = param_4;
    iVar7 = FUN_00480826(5,DAT_0047fad4,0xcf,local_24 & uVar6);
    if (iVar7 != 0) goto LAB_0047f3aa;
    FUN_00480312(5,1,&local_24);
    *puVar5 = uVar8;
    local_28 = 1;
    iVar7 = FUN_00480826(5,puVar4,0xcf,local_24);
    if (bVar2) {
      *DAT_0047fad8 = *DAT_0047fad8 & 0xfffffffe;
    }
    if (iVar7 != 0) goto LAB_0047f3aa;
    if (((((*puVar3 & 7) == (*puVar5 & 7)) && ((*puVar3 & 0xf) >> 3 == (*puVar5 & 0xf) >> 3)) &&
        ((*puVar3 >> 6 & *puVar3 >> 3 & 1) == (*puVar5 & 0x1f) >> 4)) &&
       (((*puVar3 & 0xff) >> 7 == (*puVar5 & 0x3f) >> 5 &&
        ((*DAT_0047fae0 & 0xfffffff) >> 0x1b == (*DAT_0047fae4 & 0xfffffff) >> 0x1b)))) {
      bVar2 = false;
    }
    else {
      bVar2 = true;
    }
    if (bVar2) {
      iVar7 = 1;
      goto LAB_0047f3aa;
    }
  }
  if (param_1[4] == '\0') {
    *DAT_0047fe94 = *DAT_0047fe94 | 2;
  }
  else {
    *DAT_0047fe94 = *DAT_0047fe94 & 0xfffffffd;
  }
  if (param_1[2] == '\x01') {
    *DAT_0047fe94 = *DAT_0047fe94 | 1;
  }
  else {
    if (param_1[2] != '\0') {
      iVar7 = 5;
      goto LAB_0047f3aa;
    }
    *DAT_0047fe94 = *DAT_0047fe94 & 0xfffffffe;
  }
  iVar7 = 0;
LAB_0047f3aa:
  return CONCAT44(local_28,iVar7);
}

