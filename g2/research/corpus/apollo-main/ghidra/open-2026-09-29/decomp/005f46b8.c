
undefined8 Current_Ratio(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (*(int *)(param_1 + 0x104) == 0) {
    if (*(short *)(param_1 + 300) == 0) {
      *(undefined4 *)(param_1 + 0x104) = *(undefined4 *)(param_1 + 0xf8);
    }
    else if (*(short *)(param_1 + 0x12a) == 0) {
      *(undefined4 *)(param_1 + 0x104) = *(undefined4 *)(param_1 + 0xfc);
    }
    else {
      uVar1 = TT_MulFix14(*(undefined4 *)(param_1 + 0xf8),(int)*(short *)(param_1 + 0x12a));
      uVar2 = TT_MulFix14(*(undefined4 *)(param_1 + 0xfc),(int)*(short *)(param_1 + 300));
      uVar1 = FT_Hypot(uVar1,uVar2);
      *(undefined4 *)(param_1 + 0x104) = uVar1;
    }
  }
  return CONCAT44(param_4,*(undefined4 *)(param_1 + 0x104));
}

