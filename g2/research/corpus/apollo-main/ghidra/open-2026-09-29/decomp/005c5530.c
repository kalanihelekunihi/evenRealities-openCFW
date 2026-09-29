
undefined8 FUN_005c5530(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  uVar3 = FUN_00452ef8();
  iVar4 = FUN_00452fae(uVar3);
  if (iVar4 == 0) {
    iVar4 = FUN_005c4c9c(param_1);
    if (iVar4 == 0) {
      FUN_005c499c(param_1);
    }
    else {
      FUN_005c4c44(param_1);
      if (*(int *)(param_1 + 0x44) != *(int *)(param_1 + 0x40)) {
        *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_1 + 0x40);
        local_18 = *(undefined4 *)(param_1 + 0x40);
        bVar1 = FUN_00451670(param_1,0x23,&local_18);
        if (bVar1 != 1) {
          uVar5 = (uint)bVar1;
          goto LAB_005c55b0;
        }
        FUN_00440656(param_1);
      }
      cVar2 = FUN_00452f00(uVar3);
      if (cVar2 == '\x04') {
        uVar3 = FUN_0043e1be(param_1);
        FUN_0044d510(uVar3,0);
      }
    }
  }
  else {
    *(undefined4 *)(param_1 + 0x40) = *(undefined4 *)(param_1 + 0x44);
    FUN_00440656(param_1);
  }
  uVar5 = 1;
LAB_005c55b0:
  return CONCAT44(local_18,uVar5);
}

