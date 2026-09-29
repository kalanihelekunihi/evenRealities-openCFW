
undefined4 teleprompt_page_data_update(uint *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  
  bVar7 = false;
  if (param_1 == (uint *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,0x18c,DAT_0058bc70);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058bc78,DAT_0058bc78);
    }
    uVar2 = 0;
  }
  else {
    iVar3 = page_data_lock();
    iVar1 = DAT_0058bc08;
    if (iVar3 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,400,DAT_0058bc7c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058bc80);
      }
      uVar2 = 0;
    }
    else {
      uVar6 = *param_1;
      if (uVar6 < *(uint *)(DAT_0058bc08 + 0x5190)) {
        iVar3 = semantic_page_to_slot(uVar6);
        iVar4 = semantic_slot_loaded(iVar3,uVar6);
        if (iVar4 == 0) {
          FUN_00439be4(iVar1 + iVar3 * 0x414,param_1,0x40c);
          *(undefined1 *)(iVar1 + iVar3 * 0x414 + 0x40c) = 2;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,0x1a5,DAT_0058bc94,uVar6,iVar3,
                         (short)param_1[2]);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xcc00000,DAT_0058bc98,DAT_0058bc98,uVar6,iVar3,(short)param_1[2]);
          }
          uVar5 = *(uint *)(iVar1 + 0x5194);
          if (((uVar5 <= uVar6) && (uVar6 < uVar5 + 4)) && (*(int *)(iVar1 + 0x5198) == 0)) {
            bVar7 = *(int *)(iVar1 + 0x5190) != 0;
            for (uVar6 = uVar5;
                ((bVar7 && (uVar6 < uVar5 + 4)) && (uVar6 < *(uint *)(iVar1 + 0x5190)));
                uVar6 = uVar6 + 1) {
              uVar2 = semantic_page_to_slot(uVar6);
              iVar3 = semantic_slot_loaded(uVar2,uVar6);
              if (iVar3 == 0) {
                bVar7 = false;
              }
            }
            if (bVar7) {
              *(undefined4 *)(iVar1 + 0x5198) = 1;
            }
          }
          semantic_page_data_unlock();
          if (bVar7) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,0x1bc,DAT_0058bc9c);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_0058bca0,DAT_0058bca0);
            }
            FUN_00589b68(5,0);
          }
          uVar2 = 1;
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,0x19d,DAT_0058bc8c,uVar6,iVar3);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_0058bc90,DAT_0058bc90,uVar6,iVar3);
          }
          semantic_page_data_unlock();
          uVar2 = 0;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc74,0x196,DAT_0058bc84,uVar6,
                       *(int *)(iVar1 + 0x5190) + -1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0058bc88,DAT_0058bc88,uVar6,
                              *(int *)(iVar1 + 0x5190) + -1);
        }
        semantic_page_data_unlock();
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

