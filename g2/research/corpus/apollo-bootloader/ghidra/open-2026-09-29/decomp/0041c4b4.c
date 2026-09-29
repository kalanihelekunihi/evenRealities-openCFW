
/* WARNING: Type propagation algorithm not settling */

undefined8 FUN_0041c4b4(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint *puVar2;
  int *piVar3;
  char *pcVar4;
  uint *puVar5;
  uint *puVar6;
  int iVar7;
  uint local_18 [3];
  
  local_18[1] = 0;
  local_18[0] = param_2 & 0xffffff00;
  if ((int)(*DAT_0041cb24 << 0x1e) < 0) {
    *DAT_0041cb24 = *DAT_0041cb24 & 0xfffffffb;
  }
  local_18[2] = param_4;
  if (*DAT_0041cb28 == '\0') {
    FUN_0042252e();
    FUN_0041c17a(0x1c);
    puVar2 = DAT_0041cb14;
    *DAT_0041cb14 = *DAT_0041cb14 & 0xfffffffe;
    *puVar2 = *puVar2 & 0xfffffff1;
  }
  FUN_0041c9ca(*DAT_0041cb2c);
  *DAT_0041cb30 = *DAT_0041cb30 | 1;
  if ((*DAT_0041cb18 << 0x1c < 0) && (FUN_0041c2d8(0x1d,local_18), (char)local_18[0] == '\0')) {
    FUN_0041bf84(0x1d);
  }
  FUN_0041b918(local_18 + 1);
  FUN_0041c320();
  piVar3 = DAT_0041cb1c;
  if ((*DAT_0041cb1c == DAT_0041cb20) ||
     ((iVar7 = FUN_00421548(1,0x210,1,DAT_0041cb1c + 0xd), iVar7 == 0 &&
      (iVar7 = FUN_00421548(1,0x245,1,piVar3 + 0x11), iVar7 == 0)))) {
    FUN_0041ce52();
    FUN_0041c17a(0x17);
    FUN_0041c17a(0x1d);
    puVar2 = DAT_0041cb04;
    if (0x21 < (*DAT_0041cb04 & 0xff)) {
      *DAT_0041cb34 = 1;
    }
    FUN_0041bbd0(DAT_0041cb34);
    FUN_0041be36(DAT_0041cb38);
    *DAT_0041cb3c = (*DAT_0041cb3c | 0xf80000 | DAT_0041cb40) & 0xffffbfff;
    *DAT_0041cb44 = 0;
    *DAT_0041cb48 = *DAT_0041cb48 & 0xffff00ff | 0x400;
    puVar5 = DAT_0041cb50;
    pcVar4 = DAT_0041cb4c;
    if (*DAT_0041cb4c == '\0') {
      *DAT_0041cb54 = (*DAT_0041cb50 & 0x3ffffff) >> 0x14;
      puVar6 = DAT_0041cb58;
      *DAT_0041cb5c = *DAT_0041cb58 & 0x3f;
      *DAT_0041cb60 = *puVar5 >> 0x1a;
      *DAT_0041cb64 = (*puVar6 & 0xffffff) >> 0x12;
      *DAT_0041cb6c = *DAT_0041cb68 & 0x7f;
      *DAT_0041cb74 = *DAT_0041cb70 & 0x7f;
      *DAT_0041cb7c = (*DAT_0041cb78 & 0x7fffffff) >> 0x1d;
      puVar5 = DAT_0041cb80;
      *DAT_0041cb84 = (*DAT_0041cb80 & 0x3fff) >> 10;
      puVar6 = DAT_0041cb88;
      *DAT_0041cb88 = *puVar5 & 0x3ff;
      if (((*DAT_0041cb8c & 0x3f) >> 4 == 3) &&
         ((((*puVar2 & 0xff) == 0x21 && (*DAT_0041cb90 != 0)) || (0x21 < (*puVar2 & 0xff))))) {
        bVar1 = true;
      }
      else {
        bVar1 = false;
      }
      if (bVar1) {
        if (((((*puVar2 & 0xff) == 0x21) && (2 < *DAT_0041cb90)) ||
            (((*puVar2 & 0xff) == 0x22 && (*DAT_0041cb90 == 1)))) ||
           (((*puVar2 & 0xff) == 0x23 && (*DAT_0041cb90 == 0)))) {
          *puVar6 = *puVar6 + 7;
        }
        else if ((((*puVar2 & 0xff) == 0x21) && (*DAT_0041cb90 < 3)) ||
                (((*puVar2 & 0xff) == 0x22 && (*DAT_0041cb90 == 0)))) {
          *puVar6 = *puVar6 + 6;
        }
      }
      *DAT_0041cb98 = *DAT_0041cb94;
      puVar5 = DAT_0041cb9c;
      *DAT_0041cba0 = (*DAT_0041cb9c & 0x3fffffff) >> 0x19;
      *DAT_0041cba4 = (*puVar5 & 0xffff) >> 0xb;
      puVar5 = DAT_0041cba8;
      *DAT_0041cbac = (*DAT_0041cba8 & 0x3fffffff) >> 0x19;
      *DAT_0041cbb0 = (*puVar5 & 0xffff) >> 0xb;
      *DAT_0041cbb8 = (*DAT_0041cbb4 & 0x1fff) >> 8;
      *DAT_0041cbc0 = (*DAT_0041cbbc & 0x3fffff) >> 0x11;
      *pcVar4 = '\x01';
    }
    *DAT_0041cbc4 = *DAT_0041cbc4 | 0x40000000;
    puVar5 = DAT_0041cbc8;
    *DAT_0041cbc8 = *DAT_0041cbc8 | 0x10000;
    *puVar5 = *puVar5 | 0x1000;
    local_18[2] = critical_save();
    FUN_0041cdca();
    FUN_0041cde0(0,*DAT_0041cbcc);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_18[2] & 1) == 1);
    }
    FUN_0041ce10(local_18[2]);
    FUN_0041acb2();
    if (0x21 < (*puVar2 & 0xff)) {
      *DAT_0041cbd0 = *DAT_0041cbd0 | 6;
    }
    iVar7 = 0;
  }
  return CONCAT44(local_18[0],iVar7);
}

