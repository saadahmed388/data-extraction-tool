from pydantic import BaseModel

############# Connection Models ################

class NewConnectionPayload(BaseModel):
    name: str
    user: str
    password: str
    dsn: str

class RemoveConnectionPayload(BaseModel):
    id: str
    name: str

class UpdateConnectionPayload(BaseModel):
    id: str
    name: str
    user: str
    password: str
    dsn: str

############# Query Models #############

class NewQueryPayload(BaseModel):
    name: str
    sql: str
    query_class: str

class UpdateQueryClassPayload(BaseModel):
    id: str
    query_class: str

class UpdateQueryPayload(BaseModel):
    id: str
    name: str
    sql: str

class RemoveQueryPayload(BaseModel):
    id: str
    name: str

############## Preset Models ############

class NewPresetPayload(BaseModel):
    name: str

class UpdatePresetPayload(BaseModel):
    id: str
    old_name: str
    new_name: str

class RemovePresetPayload(BaseModel):
    id: str
    name: str

class NewPresetItemPayload(BaseModel):
    con_id: str
    query_id: str
    preset_id: str
    con_name:str
    query_name: str
    preset_name: str
    

class UpdatePresetItemPayload(BaseModel):
    preset_item_id: str
    con_id: str
    query_id: str
    preset_id: str
    con_name: str
    query_name: str
    preset_name: str

class RemovePresetItemPayload(BaseModel):
    preset_item_id: str
    preset_id: str
    preset_name: str


############### Export Configuration Models ###############

class NewConfigPayload(BaseModel):
    name: str

class RemoveConfigPayload(BaseModel):
    id: str
    name: str  

class UpdateConfigPayload(BaseModel):
    id: str
    old_name: str  
    new_name: str

class UpdateConfigPresetListPayload(BaseModel):
    config_id: str
    preset_list : dict
    preset_id : str
    preset_name: str
    mode: str


############### SR Models ####################

class NewSRPayload(BaseModel):
    sr_num: str
    export_config_id: str
    export_config_name: str

class UpdateSRPayload(BaseModel):
    sr_id: str
    old_sr_num: str
    new_sr_num: str

class RemoveSRPayload(BaseModel):
    sr_id: str  
    sr_num: str

class UpdateSRConfigPayload(BaseModel):
    sr_id: str
    export_config_id: str
    export_config_name: str
