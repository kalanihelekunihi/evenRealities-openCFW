
/* WARNING: Removing unreachable block (ram,0x0056d70c) */
/* WARNING: Removing unreachable block (ram,0x0056d722) */
/* WARNING: Removing unreachable block (ram,0x0056d750) */
/* WARNING: Removing unreachable block (ram,0x0056d758) */
/* WARNING: Removing unreachable block (ram,0x0056d78e) */
/* WARNING: Removing unreachable block (ram,0x0056d796) */
/* WARNING: Removing unreachable block (ram,0x0056d7c4) */
/* WARNING: Removing unreachable block (ram,0x0056d7ec) */
/* WARNING: Removing unreachable block (ram,0x0056d7f4) */
/* WARNING: Removing unreachable block (ram,0x0056d802) */
/* WARNING: Removing unreachable block (ram,0x0056d7cc) */
/* WARNING: Removing unreachable block (ram,0x0056d7d4) */
/* WARNING: Removing unreachable block (ram,0x0056d7ea) */
/* WARNING: Removing unreachable block (ram,0x0056d7a4) */
/* WARNING: Removing unreachable block (ram,0x0056d7ac) */
/* WARNING: Removing unreachable block (ram,0x0056d7c2) */
/* WARNING: Removing unreachable block (ram,0x0056d76e) */
/* WARNING: Removing unreachable block (ram,0x0056d776) */
/* WARNING: Removing unreachable block (ram,0x0056d78c) */
/* WARNING: Removing unreachable block (ram,0x0056d730) */
/* WARNING: Removing unreachable block (ram,0x0056d738) */
/* WARNING: Removing unreachable block (ram,0x0056d74e) */

void smpLogByteArray(undefined4 param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  int iVar4;
  int iVar5;
  char local_218 [512];
  
  iVar5 = 0;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,&DAT_0056d760,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,DAT_0056d83c,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,DAT_0056d82c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0056d6c8,&DAT_0056d814,3), iVar1 != 0)) {
            WsfTrace(DAT_0056d82c,param_1);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2c7,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2c7,param_1);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2c7,param_1);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2c7,param_1);
    }
  }
  while (iVar5 < (int)(param_3 & 0xff)) {
    iVar1 = 0x10;
    if ((int)((param_3 & 0xff) - iVar5) < 0x10) {
      iVar1 = iVar5;
    }
    local_218[0] = '[';
    iVar4 = 1;
    for (uVar2 = 0; (int)uVar2 < iVar1; uVar2 = uVar2 + 1) {
      if ((uVar2 != 0) && ((uVar2 & 3) == 0)) {
        local_218[iVar4] = ' ';
        iVar4 = iVar4 + 1;
      }
      bVar3 = *(byte *)(param_2 + iVar5) >> 4;
      if (bVar3 < 10) {
        local_218[iVar4] = bVar3 + 0x30;
      }
      else {
        local_218[iVar4] = bVar3 + 0x57;
      }
      bVar3 = *(byte *)(param_2 + iVar5) & 0xf;
      if (bVar3 < 10) {
        local_218[iVar4 + 1] = bVar3 + 0x30;
      }
      else {
        local_218[iVar4 + 1] = bVar3 + 0x57;
      }
      iVar4 = iVar4 + 2;
      iVar5 = iVar5 + 1;
    }
    local_218[iVar4] = ']';
    local_218[iVar4 + 1] = '\0';
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,&DAT_0056d760,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,DAT_0056d83c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056d82c,DAT_0056d82c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0056d6c8,&DAT_0056d814,3), iVar1 != 0)) {
              WsfTrace(DAT_0056d82c,local_218);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2ea,local_218);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0056d818,DAT_0056d838,DAT_0056d8c0,0x2ea,local_218);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2ea,local_218);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0056d6c8,DAT_0056d838,DAT_0056d8c0,0x2ea,local_218);
      }
    }
  }
  return;
}

