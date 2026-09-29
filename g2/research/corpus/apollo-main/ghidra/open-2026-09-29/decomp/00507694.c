
undefined4 FUN_00507694(int param_1,char param_2,char param_3)

{
  undefined4 uVar1;
  
  if (param_2 == '\0') {
    *(byte *)(param_1 + 0x12) = *(byte *)(param_1 + 0x12) & 0xfd;
  }
  else {
    *(byte *)(param_1 + 0x12) = *(byte *)(param_1 + 0x12) | 2;
  }
  if (param_3 == '\0') {
    *(byte *)(param_1 + 0x12) = *(byte *)(param_1 + 0x12) & 0xfe;
  }
  else {
    *(byte *)(param_1 + 0x12) = *(byte *)(param_1 + 0x12) | 1;
  }
  uVar1 = FUN_00508e92(param_1,0x1be,1,param_1 + 0x12);
  return uVar1;
}

