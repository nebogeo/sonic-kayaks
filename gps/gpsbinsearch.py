import os, struct

def check_buffer(search,buf):
    cp = len(buf)/2
    found = True
    for i in range(0,len(search)):
        if found and buf[cp+i]!=struct.unpack('B',search[i])[0]:
            found = False
    if found:
        try:
            print(buf.decode("utf-8"))
        except:
            pass
        print(''.join('0x{:02x} '.format(x) for x in buf))
        #exit(1)

def decode_buffer(buf):
    if buf[0]==0xb5 and buf[1]==0x62:
        print("Class: "+''.join('0x{:02x}'.format(buf[2]))+
              " ID: "+''.join('0x{:02x}'.format(buf[3]))+
              " Len: "+''.join('0x{:02x}'.format(buf[4]))+
              " "+''.join('0x{:02x}'.format(buf[5]))+
              " Size: "+str(buf[4]+(buf[5]<<8)))

def run():
    buf_len=500
    buf = bytearray()
    for i in range(0,buf_len):
        buf.append(0)

    with open("/dev/ttyUSB0","rb") as f:
        while 1:
            c = f.read(1)
            #print(c)
            if c:
                bin = struct.unpack('B',c)[0]
                if bin:
                    buf.append(bin)
                    buf=buf[-buf_len:]
                    check_buffer("jRD",buf)
                    #check_buffer("B562".decode("hex"),buf)
                    decode_buffer(buf)
                    #check_buffer("unknown",buf)                                
                    #print(buf)
                    #print(''.join('0x{:02x} '.format(x) for x in buf))

#run()

#print("6a65c589628a628a9a62828a629a8a628a92ba6262829a62b2aa6282b2aa626282b2629aaa629a8292626282ca629a92628acab262628252b28a6aa444e90aead495158913491329d31329531329531329ab53138929931309eb1369d313268929931309531309d3d3138929d31389536292aa8262628252b21ad5a488e914d5d495158913691329d31329136282ba628a92ca62628aca62a2c26292bab26262929262a2a26282baba6262929a62b292628aaaba62628252b2aa6a52443a05756a65c58962a2628a9a629a8a628ab26282a2ba62628252aa8a6aa444e98aead4951569132913291313c9536282ca6282a2c26262ba8262b2ba62829ab26262ba8a62aaaa6292a2826262ba926282ba62929a9262628252ba926aa444748aead4951569134913298262bac26282ca629aaac26262baca628a926282a2ba6262c2826282826282caaa6262c2aa62a2ca628ab2ca62628252baaa6aa444e98aead495156983691329131309b262b2a2629a82b26262c2ba6282c2629a92ca62628252ba2ad5a444e92ad4d42a154993291309136282a26282b26292929a626282ba628aa26282aa8262628a8a628a9a629a8aa26262".decode("hex"))

                
print("baba6262c2aa62928a628abaa26262c2b262b2ba62929a9a6262c2ba629a8a629a92b262929a628252baaa6aa444e92aead495154913291309d31309131349931349d39326892953134909629a8a9a62628a9262b2c26292a2b262628aca62c282629282aa62628252bab26aa444e92ad4d49a154913499309d31349d31309d31309138262629a826282ba62829a9a62629a9a629ab2628ab2b26292ca628252a2b26aa444e9caea148a8aa9828a827282ba82b2826272c58282aa82aa72c2b28a82ba62bac58aaaa2caa2ca728282620ab10aa9b21ad5a488e994ea6a151529531353275327098262a2826262626292ca62aa8262a2ca52b2a26a52443ae5a5452a8a2953135327532709131309d31309536292828aca62828262828252ba1ad5a488e994ea94d42a295313532753270913134953729a62aa82729a62a2ca729a62626262626252b2126ba444e9ca8a1545c5098a62828a628292620ae5453545158a5535d57ab5a549aa6aa444e9ca4a556a1429531353a713260913132914a91353262609d353262613c98a09135313a69309b2aa9a8262bac58272aaaaa26262829a82ca8aca6262620ac5b2a982826aa444e9caca15d51489891589a98a0993a9aaa26272c58a728292b2625a650aa59a1a3552223ae575ea2a1429531353531326091313a91353262609d353262613c98a".decode("hex"))
