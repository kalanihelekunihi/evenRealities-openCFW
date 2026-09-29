
int FUN_00420c5c(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  byte local_14 [4];
  undefined4 uStack_10;
  
  if (*DAT_00421010 == 0) {
    iVar1 = 2;
  }
  else {
    uStack_10 = param_4;
    FUN_004207f4();
    iVar1 = FUN_004205f4(5,0,0,local_14,1);
    if (iVar1 == 0) {
      if (((local_14[0] >> 6 & 1) == param_1) && ((local_14[0] & 0x3c) == 0)) {
        elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x52a,DAT_0042107c);
        iVar1 = 0;
      }
      else {
        iVar1 = FUN_00420984();
        if (iVar1 == 0) {
          if (param_1 == 0) {
            local_14[0] = local_14[0] & 0xbf;
          }
          else {
            local_14[0] = local_14[0] | 0x40;
          }
          local_14[0] = local_14[0] & 0xc3;
          iVar1 = FUN_0042069e(1,0,0,local_14,1);
          if (iVar1 == 0) {
            FUN_004207f4();
            iVar1 = FUN_004205f4(5,0,0,local_14,1);
            if (iVar1 == 0) {
              if ((local_14[0] >> 6 & 1) == param_1) {
                iVar1 = 0;
              }
              else {
                puVar2 = DAT_0042108c;
                if (param_1 != 0) {
                  puVar2 = &DAT_00420f6c;
                }
                elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x550,DAT_00421090,puVar2);
                iVar1 = 1;
              }
            }
            else {
              elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x54a,DAT_00421088);
            }
          }
          else {
            elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x540,DAT_00421084);
          }
        }
        else {
          elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x531,DAT_00421080);
        }
      }
    }
    else {
      elog_output(2,DAT_00421034,DAT_00421030,DAT_00421078,0x521,DAT_00421074);
    }
  }
  return iVar1;
}

