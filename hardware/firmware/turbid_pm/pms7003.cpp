// Sonic Kayaks Copyright (C) 2020 FoAM Kernow
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include "pms7003.h"
#include <string.h>

short swap_endian(short in) {
  return (in>>8) | (in<<8);
}


void pms7003_build_command(pms7003_command *cmd, unsigned char type, unsigned char data) {
  cmd->id=pms7003_id;
  cmd->cmd=type;
  cmd->data_h=0;
  cmd->data_l=data;
  short total=0;
  for (unsigned int i=0; i<5; i++) {
    total+=((unsigned char*)cmd)[i];
  }
  cmd->verify=swap_endian(total);  
}

void pms7003_stream_init(pms7003_stream *s) {
  s->msg_ready=0;
  s->write_pos=0;
  s->msg_size=0;
}

unsigned char pms7003_id_check(unsigned char *data, unsigned long data_size) {
  if (data_size<2 || data[0]!=(pms7003_id&0x00ff) || data[1]!=(pms7003_id>>8)) {
    return 0;
  }
  return 1;
}

void pms7003_stream_update(pms7003_stream *s, unsigned char *data, unsigned long data_size) {
  // too big to add
  if (data_size>pms7003_STREAM_SIZE) {
    return;
  }

  // is this the start of a new message?
  if (pms7003_id_check(data,data_size)) { 
    // if we have a message in the stream
    if (s->write_pos>0) { 
      // copy it to the msg area and set msg size
      memcpy(s->msg,s->stream,s->write_pos); 
      s->msg_size=s->write_pos;
      s->msg_ready=1;
      // reset the stream
      s->write_pos=0;
    }
    // add to the stream
    memcpy(s->stream+s->write_pos,data,data_size); 
    s->write_pos+=data_size;
  } else {
    // only add this (intermediate message) if we are already writing
    // otherwise it's junk
    if (s->write_pos>0) {
      // add to the stream
      memcpy(s->stream+s->write_pos,data,data_size); 
      s->write_pos+=data_size;
    }
  }
  
  if (s->write_pos>=pms7003_STREAM_SIZE) { // max size reached
    // copy it to the msg area and set msg size
    memcpy(s->msg,s->stream,s->write_pos); 
    s->msg_ready=1;
    s->msg_size=s->write_pos;
    // reset the stream
    s->write_pos=0;
  }
  
}


/////////////////////////////////////////////
