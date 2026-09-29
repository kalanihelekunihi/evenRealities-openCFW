
undefined8 FUN_00491be4(int param_1,uint param_2,undefined *param_3)

{
  byte bVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  
  uVar5 = param_2;
  if ((99 < *(ushort *)(param_1 + 0x12)) && (*(char *)(param_1 + 0x10) != '\0')) {
    *(undefined1 *)(param_1 + 0x10) = 0;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar5 = 0x251;
      param_3 = PTR_s__TF___error_Parser_timeout_00491f30;
      FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_AcceptChar_00491f34);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__TinyFrame__TF___error_Parser_ti_00491f38);
    }
  }
  *(undefined2 *)(param_1 + 0x12) = 0;
  bVar1 = *(byte *)(param_1 + 0x10);
  if (bVar1 == 0) {
    if ((param_2 & 0xff) == 1) {
      FUN_00491bb6(param_1);
    }
  }
  else {
    uVar2 = (ushort)param_2;
    if (bVar1 == 2) {
      *(ushort *)(param_1 + 0x601c) = uVar2 & 0xff | *(short *)(param_1 + 0x601c) << 8;
      *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      if (*(short *)(param_1 + 0x6018) == 2) {
        uVar3 = FUN_0049174e(*(undefined2 *)(param_1 + 0x601a));
        *(undefined2 *)(param_1 + 0x601a) = uVar3;
        if (*(short *)(param_1 + 0x601a) == *(short *)(param_1 + 0x601c)) {
          if (*(short *)(param_1 + 0x16) == 0) {
            FUN_004919e8(param_1);
            *(undefined1 *)(param_1 + 0x10) = 0;
          }
          else {
            *(undefined1 *)(param_1 + 0x10) = 5;
            *(undefined2 *)(param_1 + 0x6018) = 0;
            uVar3 = FUN_0049172c();
            *(undefined2 *)(param_1 + 0x601a) = uVar3;
            if (0x6000 < *(ushort *)(param_1 + 0x16)) {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                uVar5 = 0x2a5;
                param_3 = PTR_s__TF___error_Rx_payload_too_long__00491f44;
                FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_AcceptChar_00491f34,0x2a5,
                             PTR_s__TF___error_Rx_payload_too_long__00491f44,
                             *(undefined2 *)(param_1 + 0x16));
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0x4400000,PTR_s__TinyFrame__TF___error_Rx_payloa_00491f48,
                                    PTR_s__TinyFrame__TF___error_Rx_payloa_00491f48,
                                    *(undefined2 *)(param_1 + 0x16));
              }
              *(undefined1 *)(param_1 + 0x6020) = 1;
            }
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            uVar5 = 0x292;
            param_3 = PTR_s__TF___error_Rx_head_cksum_mismat_00491f3c;
            FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_AcceptChar_00491f34);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__TinyFrame__TF___error_Rx_head_c_00491f40,
                                PTR_s__TinyFrame__TF___error_Rx_head_c_00491f40);
          }
          *(undefined1 *)(param_1 + 0x10) = 0;
        }
      }
    }
    else if (bVar1 < 2) {
      uVar3 = FUN_00491730(*(undefined2 *)(param_1 + 0x601a),param_2 & 0xff);
      *(undefined2 *)(param_1 + 0x601a) = uVar3;
      *(ushort *)(param_1 + 0x16) = uVar2 & 0xff | *(short *)(param_1 + 0x16) << 8;
      *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      if (*(short *)(param_1 + 0x6018) == 2) {
        *(undefined1 *)(param_1 + 0x10) = 4;
        *(undefined2 *)(param_1 + 0x6018) = 0;
      }
    }
    else if (bVar1 == 4) {
      uVar3 = FUN_00491730(*(undefined2 *)(param_1 + 0x601a),param_2 & 0xff);
      *(undefined2 *)(param_1 + 0x601a) = uVar3;
      *(ushort *)(param_1 + 0x601e) = uVar2 & 0xff | *(short *)(param_1 + 0x601e) << 8;
      *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      if (*(short *)(param_1 + 0x6018) == 2) {
        *(undefined1 *)(param_1 + 0x10) = 2;
        *(undefined2 *)(param_1 + 0x6018) = 0;
        *(undefined2 *)(param_1 + 0x601c) = 0;
      }
    }
    else if (bVar1 < 4) {
      uVar3 = FUN_00491730(*(undefined2 *)(param_1 + 0x601a),param_2 & 0xff);
      *(undefined2 *)(param_1 + 0x601a) = uVar3;
      *(ushort *)(param_1 + 0x14) = uVar2 & 0xff | *(short *)(param_1 + 0x14) << 8;
      *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      if (*(short *)(param_1 + 0x6018) == 2) {
        *(undefined1 *)(param_1 + 0x10) = 1;
        *(undefined2 *)(param_1 + 0x6018) = 0;
      }
    }
    else if (bVar1 == 6) {
      *(ushort *)(param_1 + 0x601c) = uVar2 & 0xff | *(short *)(param_1 + 0x601c) << 8;
      *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      if (*(short *)(param_1 + 0x6018) == 2) {
        uVar3 = FUN_0049174e(*(undefined2 *)(param_1 + 0x601a));
        *(undefined2 *)(param_1 + 0x601a) = uVar3;
        if (*(char *)(param_1 + 0x6020) == '\0') {
          if (*(short *)(param_1 + 0x601a) == *(short *)(param_1 + 0x601c)) {
            FUN_004919e8(param_1);
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              uVar5 = 0x2ca;
              param_3 = PTR_s__TF___error_Body_cksum_mismatch_00491f4c;
              FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_AcceptChar_00491f34);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__TinyFrame__TF___error_Body_cksu_00491f50,
                                  PTR_s__TinyFrame__TF___error_Body_cksu_00491f50);
            }
          }
        }
        *(undefined1 *)(param_1 + 0x10) = 0;
      }
    }
    else if (bVar1 < 6) {
      if (*(char *)(param_1 + 0x6020) == '\0') {
        uVar3 = FUN_00491730(*(undefined2 *)(param_1 + 0x601a),param_2 & 0xff);
        *(undefined2 *)(param_1 + 0x601a) = uVar3;
        uVar2 = *(ushort *)(param_1 + 0x6018);
        *(ushort *)(param_1 + 0x6018) = uVar2 + 1;
        *(char *)(param_1 + (uint)uVar2 + 0x18) = (char)param_2;
      }
      else {
        *(short *)(param_1 + 0x6018) = *(short *)(param_1 + 0x6018) + 1;
      }
      if (*(short *)(param_1 + 0x6018) == *(short *)(param_1 + 0x16)) {
        *(undefined1 *)(param_1 + 0x10) = 6;
        *(undefined2 *)(param_1 + 0x6018) = 0;
        *(undefined2 *)(param_1 + 0x601c) = 0;
      }
    }
  }
  return CONCAT44(param_3,uVar5);
}

