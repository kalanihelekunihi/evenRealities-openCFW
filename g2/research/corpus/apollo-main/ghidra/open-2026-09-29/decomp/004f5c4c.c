
undefined8 FUN_004f5c4c(undefined4 param_1,undefined4 param_2)

{
  ushort *puVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  ushort uVar7;
  uint uVar8;
  uint uVar9;
  ushort uVar10;
  int iVar11;
  
  *DAT_004f62f4 = '\x04';
  *DAT_004f62f8 = 0;
  puVar1 = DAT_004f6760;
  iVar5 = DAT_004f62f0;
  if (*(char *)(DAT_004f62f0 + 0x1220) == '\0') {
    uVar2 = 5;
  }
  else {
    uVar10 = 0;
    uVar7 = *DAT_004f6760;
    uVar8 = 0;
    uVar9 = 0;
    if (uVar7 == 0) {
      uVar7 = 0;
      while ((uVar7 < 0x14 && (uVar10 < 0x28))) {
        if (*(char *)((uint)uVar7 * 0xe8 + iVar5 + 0xe4) != '\0') {
          FUN_004f55e0(iVar5 + (uint)uVar7 * 0xe8,puVar1 + (uint)uVar10 * 0x94 + 4);
          uVar10 = uVar10 + 1;
        }
        uVar7 = uVar7 + 1;
      }
      *DAT_004f62f4 = '\x01';
      uVar8 = (uint)uVar10;
    }
    else {
      for (iVar11 = 0; iVar11 < 0x14; iVar11 = iVar11 + 1) {
        if (*(char *)(iVar11 * 0xe8 + iVar5 + 0xe4) != '\0') {
          iVar3 = FUN_004f5636(*(undefined4 *)(iVar5 + iVar11 * 0xe8));
          if (iVar3 < 0) {
            *DAT_004f62f4 = '\x02';
            uVar9 = uVar9 + 1;
            for (uVar4 = (uint)uVar7; 0 < (int)uVar4; uVar4 = uVar4 - 1) {
              if (uVar7 < 0x28) {
                uVar6 = 0;
                do {
                  *(undefined1 *)((int)puVar1 + uVar6 + uVar4 * 0x128 + 8) =
                       *(undefined1 *)((int)puVar1 + uVar6 + uVar4 * 0x128 + -0x120);
                  uVar6 = uVar6 + 1;
                } while (uVar6 < 0x128);
              }
            }
            FUN_004f55e0(iVar5 + iVar11 * 0xe8,puVar1 + 4);
          }
          else {
            FUN_004f55e0(iVar5 + iVar11 * 0xe8,puVar1 + iVar3 * 0x94 + 4);
            uVar8 = uVar8 + 1;
          }
          if (uVar7 < 0x28) {
            uVar10 = uVar10 + 1;
          }
        }
      }
    }
    if ((*DAT_004f62f4 == '\x04') || (*DAT_004f62f4 == '\x01')) {
      *DAT_004f62f8 = uVar8;
    }
    else if (*DAT_004f62f4 == '\x02') {
      *DAT_004f62f8 = uVar9;
    }
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 0x3d7;
      FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f6768,0x3d7,DAT_004f6764,uVar10);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__quicklist_page_Modify__total____004f6864,
                          PTR_s__quicklist_page_Modify__total____004f6864,uVar10);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

