
/* WARNING: Type propagation algorithm not settling */

undefined8 FUN_0047fae8(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

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
  if ((int)(*DAT_00480120 << 0x1e) < 0) {
    *DAT_00480120 = *DAT_00480120 & 0xfffffffb;
  }
  local_18[2] = param_4;
  if (*DAT_00480124 == '\0') {
    FUN_004d403e();
    FUN_0047f7ae(0x1c);
    puVar2 = DAT_00480110;
    *DAT_00480110 = *DAT_00480110 & 0xfffffffe;
    *puVar2 = *puVar2 & 0xfffffff1;
  }
  FUN_0047ffc4(*DAT_00480128);
  *DAT_0048012c = *DAT_0048012c | 1;
  if ((*DAT_00480114 << 0x1c < 0) && (FUN_0047f90c(0x1d,local_18), (char)local_18[0] == '\0')) {
    FUN_0047f5b8(0x1d);
  }
  FUN_0047ef38(local_18 + 1);
  FUN_0047f954();
  piVar3 = DAT_00480118;
  if ((*DAT_00480118 == DAT_0048011c) ||
     ((iVar7 = FUN_004d3f3c(1,0x210,1,DAT_00480118 + 0xd), iVar7 == 0 &&
      (iVar7 = FUN_004d3f3c(1,0x245,1,piVar3 + 0x11), iVar7 == 0)))) {
    FUN_00480434();
    FUN_0047f7ae(0x17);
    FUN_0047f7ae(0x1d);
    puVar2 = DAT_00480100;
    if (0x21 < (*DAT_00480100 & 0xff)) {
      *DAT_00480130 = 1;
    }
    FUN_0047f204(DAT_00480130);
    FUN_0047f46a(DAT_00480134);
    *DAT_00480138 = (*DAT_00480138 | 0xf80000 | DAT_0048013c) & 0xffffbfff;
    *DAT_00480140 = 0;
    *DAT_00480144 = *DAT_00480144 & 0xffff00ff | 0x400;
    puVar5 = DAT_0048014c;
    pcVar4 = DAT_00480148;
    if (*DAT_00480148 == '\0') {
      *DAT_00480150 = (*DAT_0048014c & 0x3ffffff) >> 0x14;
      puVar6 = DAT_00480154;
      *DAT_00480158 = *DAT_00480154 & 0x3f;
      *DAT_0048015c = *puVar5 >> 0x1a;
      *DAT_00480160 = (*puVar6 & 0xffffff) >> 0x12;
      *DAT_00480168 = *DAT_00480164 & 0x7f;
      *DAT_00480170 = *DAT_0048016c & 0x7f;
      *DAT_00480178 = (*DAT_00480174 & 0x7fffffff) >> 0x1d;
      puVar5 = DAT_0048017c;
      *DAT_00480180 = (*DAT_0048017c & 0x3fff) >> 10;
      puVar6 = DAT_00480184;
      *DAT_00480184 = *puVar5 & 0x3ff;
      if (((*DAT_00480188 & 0x3f) >> 4 == 3) &&
         ((((*puVar2 & 0xff) == 0x21 && (*DAT_0048018c != 0)) || (0x21 < (*puVar2 & 0xff))))) {
        bVar1 = true;
      }
      else {
        bVar1 = false;
      }
      if (bVar1) {
        if (((((*puVar2 & 0xff) == 0x21) && (2 < *DAT_0048018c)) ||
            (((*puVar2 & 0xff) == 0x22 && (*DAT_0048018c == 1)))) ||
           (((*puVar2 & 0xff) == 0x23 && (*DAT_0048018c == 0)))) {
          *puVar6 = *puVar6 + 7;
        }
        else if ((((*puVar2 & 0xff) == 0x21) && (*DAT_0048018c < 3)) ||
                (((*puVar2 & 0xff) == 0x22 && (*DAT_0048018c == 0)))) {
          *puVar6 = *puVar6 + 6;
        }
      }
      *DAT_00480194 = *DAT_00480190;
      puVar5 = DAT_00480198;
      *DAT_0048019c = (*DAT_00480198 & 0x3fffffff) >> 0x19;
      *DAT_004801a0 = (*puVar5 & 0xffff) >> 0xb;
      puVar5 = DAT_004801a4;
      *DAT_004801a8 = (*DAT_004801a4 & 0x3fffffff) >> 0x19;
      *DAT_004801ac = (*puVar5 & 0xffff) >> 0xb;
      *DAT_004801b4 = (*DAT_004801b0 & 0x1fff) >> 8;
      *DAT_004801bc = (*DAT_004801b8 & 0x3fffff) >> 0x11;
      *pcVar4 = '\x01';
    }
    *DAT_004801c0 = *DAT_004801c0 | 0x40000000;
    puVar5 = DAT_004801c4;
    *DAT_004801c4 = *DAT_004801c4 | 0x10000;
    *puVar5 = *puVar5 | 0x1000;
    local_18[2] = FUN_00473940();
    FUN_004803ac();
    FUN_004803c2(0,*DAT_004801c8);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_18[2] & 1) == 1);
    }
    FUN_004803f2(local_18[2]);
    FUN_0044b158();
    if (0x21 < (*puVar2 & 0xff)) {
      *DAT_004801cc = *DAT_004801cc | 6;
    }
    iVar7 = 0;
  }
  return CONCAT44(local_18[0],iVar7);
}

