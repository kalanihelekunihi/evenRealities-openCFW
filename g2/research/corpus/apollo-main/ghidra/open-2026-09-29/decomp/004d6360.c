
char _parseWhiteListFromFS
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  uVar3 = FUN_004d58d8(1);
  iVar4 = file_open(param_1,uVar3);
  if (iVar4 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xdb,DAT_004d6aec,param_1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004d6afc,DAT_004d6afc,param_1);
    }
    *DAT_004d6b00 = 0;
    cVar2 = '\0';
  }
  else {
    uVar5 = semantic_whitelist_file_size_preserving_position(iVar4);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xe2,DAT_004d6b04,uVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d6b08,DAT_004d6b08,uVar5);
    }
    if ((int)uVar5 < 1) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xe4,DAT_004d6b0c,uVar5);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004d6b10,DAT_004d6b10,uVar5);
      }
      if (iVar4 != 0) {
        file_close(iVar4);
      }
      *DAT_004d6b00 = 0;
      cVar2 = '\0';
    }
    else {
      if (uVar5 < 0x2137) {
        iVar6 = FUN_0048e0a8();
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xed,DAT_004d6b14,uVar5);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004d6b18,DAT_004d6b18,uVar5);
        }
      }
      else {
        iVar6 = file_heap_allocate(uVar5 + 1);
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xf0,DAT_004d6b1c,uVar5);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004d6b20,DAT_004d6b20,uVar5);
        }
      }
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xf3,DAT_004d6b24);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004d6b28,DAT_004d6b28);
        }
        if (iVar4 != 0) {
          file_close(iVar4);
        }
        *DAT_004d6b00 = 0;
        cVar2 = '\0';
      }
      else {
        uVar8 = file_read(iVar6,1,uVar5,iVar4);
        uVar9 = uVar8;
        if (iVar4 != 0) {
          file_close(iVar4);
          uVar9 = 0;
        }
        if (uVar8 == uVar5) {
          iVar4 = FUN_0043d0ce(uVar9);
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0x105,DAT_004d6b34,uVar8);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004d6b38,DAT_004d6b38,uVar8);
          }
          *(undefined1 *)(iVar6 + uVar5) = 0;
          cVar2 = _parseJsonWhitelistToStruct(iVar6);
          if (cVar2 == '\0') {
            *DAT_004d6b00 = 0;
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0x114,DAT_004d6b50);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_004d6b54,DAT_004d6b54);
            }
          }
          else {
            local_1c = 0;
            FUN_0047cbc4(iVar6,uVar5,&local_1c);
            puVar1 = DAT_004d6b3c;
            *DAT_004d6b3c = local_1c;
            *DAT_004d6b00 = 1;
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0x110,DAT_004d6b40,*puVar1);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_004d6b44,DAT_004d6b44,*puVar1);
            }
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0x111,DAT_004d6b48);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004d6b4c,DAT_004d6b4c);
            }
          }
          iVar4 = FUN_0048e0a8();
          if (iVar6 != iVar4) {
            file_heap_free(iVar6);
          }
        }
        else {
          iVar4 = FUN_0043d0ce(uVar9);
          if (iVar4 << 0x1e < 0) {
            local_1c = uVar8;
            FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6af0,0xfe,DAT_004d6b2c,uVar5);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004d6b30,DAT_004d6b30,uVar5,uVar8);
          }
          iVar4 = FUN_0048e0a8();
          if (iVar6 != iVar4) {
            file_heap_free(iVar6);
          }
          *DAT_004d6b00 = 0;
          cVar2 = '\0';
        }
      }
    }
  }
  return cVar2;
}

