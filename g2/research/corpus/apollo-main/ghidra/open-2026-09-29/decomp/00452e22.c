
undefined8 FUN_00452e22(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*(int *)(param_3 + 0x10) == 0) {
    uVar2 = FUN_0044c582();
  }
  else {
    uVar2 = *(uint *)(*(int *)(param_3 + 0x10) + 0x39);
    if (param_2 != 0) {
      uVar2 = FUN_0044c54a(param_1,param_2,uVar2,*(int *)(param_3 + 0x10),uVar2,param_4);
    }
  }
  uVar1 = FUN_00441068((char)(uVar2 >> 0x10),(char)(uVar2 >> 8),uVar2 & 0xff);
  uVar1 = FUN_00482dd8(uVar1,param_4,(char)(uVar2 >> 0x18));
  return CONCAT44(uVar1,uVar1);
}

