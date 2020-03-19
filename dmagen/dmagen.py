channelTypeList = ['r', 'r', 't', 't']


import util
if __name__ == "__main__":
    channelNum = len(channelTypeList)
    x = util.fileGen.FixedOrderArbiter(channelNum)
    x.createRTL()
