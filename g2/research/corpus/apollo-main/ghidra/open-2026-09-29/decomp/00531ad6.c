
undefined8 attcExecCallback(undefined1 param_1,char param_2,uint param_3,uint param_4)

{
  undefined4 local_10;
  
  local_10 = param_3;
  if (param_2 != '\x01') {
    local_10 = 0;
    attExecCallback(param_1,param_2,param_3 & 0xffff,param_4 & 0xff);
  }
  return CONCAT44(param_4,local_10);
}

