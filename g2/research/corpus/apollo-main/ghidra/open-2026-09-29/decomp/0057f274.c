
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057f274(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  char *pcVar2;
  int iVar3;
  undefined1 auStack_454 [4];
  undefined1 auStack_450 [80];
  undefined1 auStack_400 [152];
  undefined1 auStack_368 [84];
  char acStack_314 [264];
  undefined1 auStack_20c [256];
  undefined1 auStack_10c [256];
  
  if (*_DAT_0057fc6c == 1) {
    pcVar2 = (char *)FUN_005848fc(param_3,1,auStack_454);
    if (pcVar2 == (char *)0x0) {
      FUN_004733ee(PTR_s_md5__missing_file_operand_0057fc70);
    }
    else {
      FUN_0043c0e4(auStack_10c,0xff,0);
      if (*pcVar2 == '/') {
        FUN_0044b5a0(auStack_10c,pcVar2,0xfe);
      }
      else {
        FUN_0044b728(auStack_10c,0xff,_DAT_0057f688,_DAT_0057f3c4,pcVar2);
      }
      iVar3 = FUN_0057eaa8(auStack_20c,auStack_10c);
      uVar1 = _DAT_0057f3c0;
      if (iVar3 == 0) {
        iVar3 = FUN_004cfa8a(_DAT_0057f3c0,auStack_20c,acStack_314);
        if (iVar3 == 0) {
          if (acStack_314[0] == '\x02') {
            FUN_004733ee(PTR_s_md5__cannot_calculate_hash_for_d_0057fc7c);
          }
          else {
            iVar3 = FUN_004cfa94(uVar1,auStack_368,auStack_20c,1);
            if (iVar3 == 0) {
              func_0x0059544e(auStack_400);
              while( true ) {
                FUN_0043c0e4(auStack_450 + 0x10,0x40,0);
                iVar3 = FUN_004cfb40(uVar1,auStack_368,auStack_450 + 0x10,0x40);
                if (iVar3 < 0) break;
                if (iVar3 == 0) {
                  func_0x00595608(auStack_450,auStack_400);
                  FUN_004733ee(PTR_s_MD5__s____0057fc88,auStack_20c);
                  for (iVar3 = 0; iVar3 < 0x10; iVar3 = iVar3 + 1) {
                    FUN_004733ee(_DAT_0057fc8c,auStack_450[iVar3]);
                  }
                  FUN_004733ee(0x57f684);
                  FUN_004cfad0(uVar1,auStack_368);
                  return 0;
                }
                func_0x00595578(auStack_400,auStack_450 + 0x10,iVar3);
              }
              FUN_004733ee(PTR_s_md5__file_read_error_0057fc84);
              FUN_004cfad0(uVar1,auStack_368);
            }
            else {
              FUN_004733ee(PTR_s_md5__cannot_open_file_0057fc80);
            }
          }
        }
        else {
          FUN_004733ee(PTR_s_md5__file_not_found_0057fc78);
        }
      }
      else {
        FUN_004733ee(PTR_s_md5__invalid_file_path_0057fc74);
      }
    }
  }
  return 0;
}

