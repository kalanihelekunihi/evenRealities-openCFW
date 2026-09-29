
undefined8 tracepoint_format_display_name(int param_1,uint param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (((param_3 == 0) || (param_4 == 0)) || (param_1 == 0)) {
    uVar1 = 0;
    uVar2 = param_2;
  }
  else {
    uVar2 = 0x74;
    uVar1 = FUN_0044b728(param_3,param_4,DAT_005ee890,param_2 & 0xff,0x74,param_1,param_4);
  }
  return CONCAT44(uVar2,uVar1);
}

