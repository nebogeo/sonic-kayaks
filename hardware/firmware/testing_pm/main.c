#include <stdio.h>
#include <string.h>
#include <assert.h>

const short pm7003_id=0x4d42;

#define PM7003_STREAM_SIZE 32

typedef struct {
  unsigned char msg_ready;
  unsigned int write_pos;
  unsigned char stream[PM7003_STREAM_SIZE];
  unsigned int msg_size;
  unsigned char msg[PM7003_STREAM_SIZE];
} pm7003_stream;


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

int main() {
  pm7003_stream s;

  pm7003_stream_init(&s);
  
  printf("testing strea\n");
  printf("%x %x\n",(pm7003_id&0x00ff),((pm7003_id>>8)));

  unsigned char buf[64];
  pm7003_stream_update(&s,buf,35);
  assert(s.write_pos==0);
  memcpy(buf,(char[]){0x00, 0x01, 0x03},3);
  assert(!pm7003_id_check(buf,3));
  pm7003_stream_update(&s,buf,3);
  assert(s.write_pos==0);
  memcpy(buf,(char[]){0x4d, 0x42, 0x03},3);
  assert(pm7003_id_check(buf,3));
  pm7003_stream_update(&s,buf,3);
  assert(s.write_pos==3);
  pm7003_stream_update(&s,buf,3);
  assert(s.msg_ready==1);
  assert(s.msg_size==3);
  assert(s.write_pos==3);
  s.msg_ready=0;
  // test intermediate data
  memcpy(buf,(char[]){0x04, 0x05, 0x06, 0x07, 0x08},5);
  pm7003_stream_update(&s,buf,5);
  assert(s.write_pos==8);
  assert(s.msg_ready==0);
  // reset with new message
  memcpy(buf,(char[]){0x4d, 0x42, 0x03},3);
  pm7003_stream_update(&s,buf,3);
  assert(s.msg_size==8);
  assert(s.msg_ready==1);
  assert(s.write_pos==3);
  s.msg_ready=0;
  // test tripping 32 bytes
  printf("%d\n",s.write_pos);
  // remove id byte
  memcpy(buf,(char[]){0x00, 0x42, 0x03},3);
  pm7003_stream_update(&s,buf,32-3);
  assert(s.msg_ready==1);
  assert(s.msg_size==32);
  assert(s.write_pos==0);
  s.msg_ready=0;
  // check state after 32 byte message
  memcpy(buf,(char[]){0x4d, 0x42, 0x03},3);
  pm7003_stream_update(&s,buf,3);
  assert(s.msg_ready==0); // wont be ready yet 
  pm7003_stream_update(&s,buf,3);
  assert(s.msg_size==3);
  assert(s.msg_ready==1);
  assert(s.write_pos==3);
  s.msg_ready=0;

  return 0;

}
