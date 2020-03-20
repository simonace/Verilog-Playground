from collections import namedtuple
ChannelType = namedtuple("ChannelType", ["dir", "paddr", "size"])
channelDict = {"ch0"    :  ChannelType("r", "0x12345000", 'v'),
               "ch1"    :  ChannelType("t", "0x4000ac00", 1),
               "ch2"    :  ChannelType("r", "0x50004400", 2),
               "ch3"    :  ChannelType("t", "0x4abcd800", 3)
               }


import util
if __name__ == "__main__":
    channelNum = len(channelDict)
    arb = util.fileGen.FixedOrderArbiter(channelNum)
    arb.createRtl()
    fsm = util.fileGen.ChannelFsm()
    fsm.createRtl()
