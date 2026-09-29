
void gx8002_backup_cfft(ushort *param_1,undefined4 param_2,int param_3,int param_4)

{
  ushort uVar1;
  
  uVar1 = *param_1;
  if (param_3 == 1) {
    if (uVar1 != 0x100) {
      if (uVar1 < 0x101) {
        if (uVar1 == 0x20) goto LAB_1000f26a;
        if (uVar1 < 0x21) {
          if (uVar1 != 0x10) goto joined_r0x1000f236;
        }
        else if (uVar1 != 0x40) {
          if (uVar1 != 0x80) goto joined_r0x1000f236;
          goto LAB_1000f26a;
        }
      }
      else if (uVar1 != 0x400) {
        if (uVar1 < 0x401) {
          if (uVar1 != 0x200) goto joined_r0x1000f236;
        }
        else if (uVar1 != 0x800) {
          if (uVar1 != 0x1000) goto joined_r0x1000f236;
          goto LAB_1000f28c;
        }
LAB_1000f26a:
        FUN_1000f358(param_2,uVar1,*(undefined4 *)(param_1 + 2));
        goto joined_r0x1000f236;
      }
    }
LAB_1000f28c:
    FUN_1000f610(param_2,uVar1,*(undefined4 *)(param_1 + 2),1);
    goto joined_r0x1000f236;
  }
  if (uVar1 != 0x100) {
    if (uVar1 < 0x101) {
      if (uVar1 == 0x20) goto LAB_1000f206;
      if (uVar1 < 0x21) {
        if (uVar1 != 0x10) goto joined_r0x1000f236;
      }
      else if (uVar1 != 0x40) {
        if (uVar1 != 0x80) goto joined_r0x1000f236;
        goto LAB_1000f206;
      }
    }
    else if (uVar1 != 0x400) {
      if (uVar1 < 0x401) {
        if (uVar1 != 0x200) goto joined_r0x1000f236;
      }
      else if (uVar1 != 0x800) {
        if (uVar1 != 0x1000) goto joined_r0x1000f236;
        goto LAB_1000f22c;
      }
LAB_1000f206:
      FUN_1000f2b4(param_2,uVar1,*(undefined4 *)(param_1 + 2));
      goto joined_r0x1000f236;
    }
  }
LAB_1000f22c:
  FUN_1000f3fc(param_2,uVar1,*(undefined4 *)(param_1 + 2),1);
joined_r0x1000f236:
  if (param_4 != 0) {
    FUN_1000f824(param_2,param_1[6],*(undefined4 *)(param_1 + 4));
    return;
  }
  return;
}

