
undefined8
even_ai_text_width_measure(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 == (int *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0;
    if (((*param_1 != 0) && (iVar2 = FUN_0043e2ea(*param_1), iVar2 != 0)) &&
       (iVar2 = FUN_004997f8(*param_1), iVar2 != 0)) {
      uVar1 = FUN_0044a43c();
    }
    if (((param_1[2] != 0) && (iVar2 = FUN_0043e2ea(param_1[2]), iVar2 != 0)) &&
       (iVar2 = FUN_004997f8(param_1[2]), iVar2 != 0)) {
      iVar2 = FUN_0044a43c();
      uVar1 = iVar2 + uVar1;
    }
    uVar1 = uVar1 & 0xffff;
  }
  return CONCAT44(param_4,uVar1);
}

