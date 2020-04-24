#include "pm7003.h"

short swap_endian(short in) {
  return (in>>8) | (in<<8);
}


void pm7003_build_command(pm7003_command *cmd, unsigned char type, unsigned char data) {
  cmd->id=pm7003_id;
  cmd->cmd=type;
  cmd->data_h=0;
  cmd->data_l=data;
  short total=0;
  for (unsigned int i=0; i<5; i++) {
    total+=((unsigned char*)cmd)[i];
  }
  cmd->verify=swap_endian(total);  
}
