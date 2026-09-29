
undefined8 FUN_0045fd06(int param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  undefined4 *puVar4;
  uint local_18;
  uint local_14;
  uint local_10;
  
  local_18 = param_2;
  local_14 = param_3;
  local_10 = param_4;
  if (param_1 != 0) {
    while (iVar1 = FUN_0045fc5a(param_1,&local_18), iVar1 != 0) {
      iVar1 = FUN_0045fcb2(param_1);
      if (iVar1 != 0) {
        iVar1 = FUN_0045fbd0(param_1 + 0x24);
        if (iVar1 == 0) {
          uVar2 = *(byte *)(param_1 + 0xe4) + 0xf;
          *(char *)(param_1 + 0xe4) = (char)uVar2 + (char)(uVar2 / 0x10) * -0x10;
          puVar3 = (uint *)(param_1 + 0x24 + (uint)*(byte *)(param_1 + 0xe4) * 0xc);
          *puVar3 = local_18;
          puVar3[1] = local_14;
          puVar3[2] = local_10;
          *(char *)(param_1 + 0xe6) = *(char *)(param_1 + 0xe6) + '\x01';
        }
        break;
      }
      if (local_18 == 0x3c) {
        if (((char)local_10 != '\0') && (local_14 != 0)) {
          FUN_0045f58c(param_1,local_14);
        }
      }
      else if (0x3b < local_18) {
        if (local_18 == 0x3e) {
          if (((char)local_10 != '\0') && (local_14 != 0)) {
            iVar1 = FUN_0045f840(param_1,local_14);
            if ((iVar1 == 0) || (*(char *)(iVar1 + 0xb) != '\x01')) {
              FUN_0045f58c(param_1,local_14);
            }
            else {
              FUN_0045f73a(param_1);
            }
          }
        }
        else if (local_18 < 0x3e) {
          if (((char)local_10 == '\0') || (local_14 == 0)) {
            puVar4 = (undefined4 *)FUN_0045f8e6(param_1);
            if (puVar4 != (undefined4 *)0x0) {
              FUN_0045f60e(param_1,*puVar4);
            }
          }
          else {
            FUN_0045f60e(param_1,local_14);
          }
        }
      }
      iVar1 = FUN_0045fcb2(param_1);
      if (iVar1 != 0) break;
    }
  }
  return CONCAT44(local_14,local_18);
}

