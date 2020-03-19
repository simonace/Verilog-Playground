from . import rtlWriter

class FixedOrderArbiter(object):
    def __init__(self, channelNum):
        self.channelNum = channelNum
        self.moduleName = "fixed_order_arbiter_" + str(self.channelNum) + "_channels"
        self.portList = [("clk", 'i', 'w', 1),
                         ("rstn", 'i', 'w', 1),
                         ("req", 'i', 'w', self.channelNum),
                         ("channel_available", 'i', 'w', self.channelNum),
                         ("channel_idle", 'i', 'w', self.channelNum),
                         ("allow_accept_req", 'i', 'w', self.channelNum),
                         ("start", 'o', 'w', self.channelNum)
                         ]
                         

    def createRTL(self):
        f = open(self.moduleName + ".v", "w+")
        rtlWriter.writeHeaderInfoComment(f, self.moduleName)
        f.write('\n'*2)
        rtlWriter.writeModulePortList(f, self.moduleName, self.portList)
        f.write('\n'*2)
        rtlWriter.writeRegWireLine(f, ("req_pending", 'r', self.channelNum))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("has_pend_0_to_"+str(i), 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("no_pend_0_to_"+str(i), 'w', 1))
        rtlWriter.writeRegWireLine(f, ("no_pend_all", 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("has_req_0_to_"+str(i), 'w', 1))
        for i in range(self.channelNum-1):
            rtlWriter.writeRegWireLine(f, ("no_req_0_to_"+str(i), 'w', 1))
        rtlWriter.writeRegWireLine(f, ("next_pending", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("start_from_pend", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("start_from_req", 'w', self.channelNum))
        rtlWriter.writeRegWireLine(f, ("no_busy_channel", 'w', 1))
        f.write('\n'*2)
        for i in range(self.channelNum-1):
            if i == 0:
                rtlWriter.writeAssign(f, "has_pend_0_to_0", ["req_pending[0]"])
            else:
                t = ["has_pend_0_to_"+str(i-1),'|',"req_pending["+ str(i)+"]"]
                rtlWriter.writeAssign(f, "has_pend_0_to_"+str(i), t)
            rtlWriter.writeAssign(f, "no_pend_0_to_"+str(i), ["~has_pend_0_to_"+str(i)])
        rtlWriter.writeAssign(f, "no_pend_all", ["no_pend_0_to_"+str(self.channelNum-2), "&",
                                                 "~req_pending["+str(self.channelNum-1)+"]"])
        for i in range(self.channelNum-1):
            if i == 0:
                rtlWriter.writeAssign(f, "has_req_0_to_0", ["req[0]"])
            else:
                t = ["has_req_0_to_"+str(i-1),'|',"req["+ str(i)+"]"]
                rtlWriter.writeAssign(f, "has_req_0_to_"+str(i), t)
            rtlWriter.writeAssign(f, "no_req_0_to_"+str(i), ["~has_req_0_to_"+str(i)])
        for i in range(self.channelNum):
            t = ["no_pend_all", "&", "req["+str(i)+"]"] + (["&", "no_req_0_to_"+str(i-1)] if i>0 else [])
            rtlWriter.writeAssign(f, "start_from_req["+str(i)+"]", t)
        for i in range(self.channelNum):
            t = ["req_pending["+str(i)+"]"] + (["&", "no_pend_0_to_"+str(i-1)] if i>0 else [])
            rtlWriter.writeAssign(f, "start_from_pend["+str(i)+"]", t)
        rtlWriter.writeAssign(f, "no_busy_channel", ["&channel_idle["+str(self.channelNum-1)+":0]"])
        rtlWriter.writeAssign(f, "start", ["(start_from_pend", "|", "start_from_req)", "&",
                                           "{"+str(self.channelNum)+"{no_busy_channel}}", "&",
                                           "channel_available"])
        rtlWriter.writeAssign(f, "next_pending", ["(~start)", "&", "allow_accept_req", "&",
                                                  "(req_pending", "|", "req)", "&",
                                                  "channel_available"])
        f.write('\n'*2)
        sList = [rtlWriter.IfStruct("~rstn", [rtlWriter.AssignStruct("req_pending", [str(self.channelNum) + "'h0"])]),
                 rtlWriter.ElseStruct([rtlWriter.AssignStruct("req_pending", ["next_pending"])])]
        rtlWriter.writeFlop(f, "clk", "rstn", sList, "req_pending")
        f.write("endmodule")
        
        f.close()
        
