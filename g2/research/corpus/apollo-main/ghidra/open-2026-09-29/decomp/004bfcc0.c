
undefined8
FUN_004bfcc0(int param_1,undefined4 param_2,uint param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  uint uVar2;
  uint local_20;
  undefined4 local_1c;
  
  uVar2 = 0;
  if ((param_3 & 0xff) == 0) {
    uVar2 = 0x18;
  }
  else if ((param_3 & 0xff) == 1) {
    uVar2 = 0x40;
  }
  local_20 = param_3;
  if (*(int *)(param_1 + 0x20) == 0x100) {
    iVar1 = 5;
  }
  else {
    local_1c = param_4;
    iVar1 = FUN_00538ece(*(undefined4 *)(param_1 + 0x828),uVar2 >> 3,&local_1c,&local_20);
    if (iVar1 == 0) {
      iVar1 = FUN_004bfa3c(param_1,param_3 & 0xff,local_1c,param_2);
      if (iVar1 == 0) {
        *(undefined4 *)(param_1 + (local_20 & 0xff) * 4 + 0x28) = param_4;
        *(undefined4 *)(param_1 + (local_20 & 0xff) * 4 + 0x428) = param_5;
      }
      else {
        FUN_00538f82(*(undefined4 *)(param_1 + 0x828));
      }
    }
  }
  return CONCAT44(local_20,iVar1);
}

