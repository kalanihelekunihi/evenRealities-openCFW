
undefined4 touch_config_1944_start(int *param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(char *)(*(undefined4 **)(*param_1 + 8))[1] == '\0') {
    iVar2 = Cy_MSCLP_Capture(**(undefined4 **)(*param_1 + 8),2);
    if (iVar2 == 0) {
      uVar1 = event_dispatcher(1,param_1);
    }
    else {
      uVar1 = 8;
    }
  }
  else {
    uVar1 = 0x80;
  }
  return uVar1;
}

