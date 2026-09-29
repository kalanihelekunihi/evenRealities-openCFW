
undefined8 text_stream_prepare_input(undefined4 *param_1,undefined4 param_2,char param_3)

{
  uint uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else if ((param_3 == '\0') || (param_3 == '\x02')) {
    iVar2 = FUN_0046cacc(param_2,*param_1);
    uVar1 = (uint)(iVar2 == 0);
  }
  else if (param_3 == '\x01') {
    iVar2 = FUN_0044a43c(param_2);
    uVar1 = (uint)(iVar2 == 0);
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

