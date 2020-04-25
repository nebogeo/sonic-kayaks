#include "pm7003.h"
#include <string.h>

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

void pm7003_stream_init(pm7003_stream *s) {
  s->msg_ready=0;
  s->write_pos=0;
  s->msg_size=0;
}

unsigned char pm7003_id_check(unsigned char *data, unsigned long data_size) {
  if (data_size<2 || data[1]!=(pm7003_id&0x00ff) || data[0]!=(pm7003_id>>8)) {
    return 0;
  }
  return 1;
}

void pm7003_stream_update(pm7003_stream *s, unsigned char *data, unsigned long data_size) {
  // too big to add
  if (data_size>PM7003_STREAM_SIZE) {
    return;
  }

  // is this the start of a new message?
  if (pm7003_id_check(data,data_size)) { 
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
  
  if (s->write_pos>=PM7003_STREAM_SIZE) { // max size reached
    // copy it to the msg area and set msg size
    memcpy(s->msg,s->stream,s->write_pos); 
    s->msg_ready=1;
    s->msg_size=s->write_pos;
    // reset the stream
    s->write_pos=0;
  }
  
}


/////////////////////////////////////////////
