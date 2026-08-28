/* SPDX-License-Identifier: MIT */
#include "pt_protocol_service.h"

int open_cfw_pt_firmware_service_initialize(
 struct open_cfw_pt_firmware_service *service,
 const struct open_cfw_pt_all_providers *providers,
 uint8_t *transfer_staging,size_t transfer_staging_capacity)
{
 if(service==NULL||providers==NULL||providers->basic==NULL||
    providers->config==NULL||providers->data==NULL||providers->display==NULL||
    providers->sensors==NULL||providers->services==NULL||providers->audio==NULL||
    providers->transfer==NULL)return OPEN_CFW_PT_INVALID_ARGUMENT;
 open_cfw_pt_protocol_initialize(&service->protocol);
 open_cfw_pt_transfer_initialize(&service->transfer,providers->transfer,
  transfer_staging,transfer_staging_capacity);
 if(open_cfw_pt_bind_basic_handlers(&service->protocol,providers->basic)!=0||
    open_cfw_pt_bind_config_handlers(&service->protocol,providers->config)!=0||
    open_cfw_pt_bind_data_handlers(&service->protocol,providers->data)!=0||
    open_cfw_pt_bind_display_handlers(&service->protocol,providers->display)!=0||
    open_cfw_pt_bind_sensor_handlers(&service->protocol,providers->sensors)!=0||
    open_cfw_pt_bind_service_handlers(&service->protocol,providers->services)!=0||
    open_cfw_pt_bind_audio_handlers(&service->protocol,providers->audio)!=0||
    open_cfw_pt_bind_transfer_handlers(&service->protocol,&service->transfer)!=0)
  return OPEN_CFW_PT_HANDLER_FAILED;
 return OPEN_CFW_PT_OK;
}

int open_cfw_pt_firmware_service_dispatch(
 struct open_cfw_pt_firmware_service *service,
 const uint8_t *request,uint8_t request_length,uint8_t *response,
 size_t response_capacity,uint8_t *response_length)
{
 if(service==NULL)return OPEN_CFW_PT_INVALID_ARGUMENT;
 return open_cfw_pt_protocol_dispatch(&service->protocol,request,request_length,
  response,response_capacity,response_length);
}
