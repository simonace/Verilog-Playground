CHANNEL_NUM = 4

moduleName = "fixed_order_arbiter_with_pending_" + str(CHANNEL_NUM) + "channels"

f = open(moduleName + ".v", "w+")

f.write("module " + moduleName + " (\n")
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + ''.ljust(8) + "clk".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + ''.ljust(8) + "rstn".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "req".ljust(8) + ',' + '\n')
f.write(' '*4 + "output".ljust(8) + "reg".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "grant".ljust(8) + '\n')
f.write(");\n")

f.write("\n"*2)
f.write("reg".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "req_pending".ljust(12) + ";\n")
for i in range(CHANNEL_NUM-1):
    f.write("wire".ljust(8) + ''.ljust(8) + ("has_pend_0_to_" + str(i)).ljust(12) + ";\n")
for i in range(CHANNEL_NUM-1):
    f.write("wire".ljust(8) + ''.ljust(8) + ("no_pend_0_to_" + str(i)).ljust(12) + ";\n")
f.write("wire".ljust(8) + ''.ljust(8) + "no_pend_all".ljust(12) + ";\n")
for i in range(CHANNEL_NUM-1):
    f.write("wire".ljust(8) + ''.ljust(8) + ("has_req_0_to_" + str(i)).ljust(12) + ";\n")
for i in range(CHANNEL_NUM-1):
    f.write("wire".ljust(8) + ''.ljust(8) + ("no_req_0_to_" + str(i)).ljust(12) + ";\n")
f.write("wire".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "next_pending".ljust(12) + ";\n")
f.write("wire".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "pending_grant".ljust(12) + ";\n")
f.write("wire".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "direct_grant".ljust(12) + ";\n")
f.write("wire".ljust(8) + ("[" + str(CHANNEL_NUM-1) + ":0]").ljust(8) + "next_grant".ljust(12) + ";\n")

f.write("\n"*2)
for i in range(CHANNEL_NUM-1):
    if i == 0:
        f.write("assign " + "has_pend_0_to_0".ljust(20) + " = " + "req_pending[0];" + '\n')
    else:
        f.write("assign " + ("has_pend_0_to_" + str(i)).ljust(20) + " = " + ("has_pend_0_to_" + str(i-1)) + " | req_pending[" + str(i) + "];\n")
    f.write("assign " + ("no_pend_0_to_" + str(i)).ljust(20) + " = " + "~has_pend_0_to_" + str(i) + ';\n')
f.write("assign " + "no_pend_all".ljust(20) + " = no_pend_0_to_" + str(CHANNEL_NUM-2) + " & ~req_pending[" + str(CHANNEL_NUM-1) + "];\n")
for i in range(CHANNEL_NUM-1):
    if i == 0:
        f.write("assign " + "has_req_0_to_0".ljust(20) + " = " + "req[0];" + '\n')
    else:
        f.write("assign " + ("has_req_0_to_" + str(i)).ljust(20) + " = " + ("has_req_0_to_" + str(i-1)) + " | req[" + str(i) + "];\n")
    f.write("assign " + ("no_req_0_to_" + str(i)).ljust(20) + " = " + "~has_req_0_to_" + str(i) + ';\n')
for i in range(CHANNEL_NUM):
    if i == 0:
        f.write("assign " + ("direct_grant[" + str(i) + "]").ljust(20) + " = no_pend_all & req[0];\n")
    else:
        f.write("assign " + ("direct_grant[" + str(i) + "]").ljust(20) + " = no_pend_all & no_req_0_to_" + str(i-1) + "& req[" + str(i) + "];\n")
for i in range(CHANNEL_NUM):
    if i == 0:
        f.write("assign " + ("pending_grant[" + str(i) + "]").ljust(20) + " = req_pending[0];\n")
    else:
        f.write("assign " + ("pending_grant[" + str(i) + "]").ljust(20) + " = no_pend_all & no_pend_0_to_" + str(i-1) + "& req_pending[" + str(i) + "];\n")
f.write("assign " + "next_grant".ljust(20) + " = pending_grant | direct_grant;\n")
f.write("assign " + "next_pending".ljust(20) + " = (~next_grant) & ( req_pending | req);\n\n")

f.write("always @(posedge clk or negedge rstn) begin\n")
f.write(' '*4 + "if (~rstn) begin\n")
f.write(' '*8 + "grant <= " + str(CHANNEL_NUM) + "`b0;\n")
f.write(' '*4 + "end\n")
f.write(' '*4 + "else begin\n")
f.write(' '*8 + "grant <= next_grant;\n")
f.write(' '*4 + "end\n")
f.write("end\n\n")
f.write("always @(posedge clk or negedge rstn) begin\n")
f.write(' '*4 + "if (~rstn) begin\n")
f.write(' '*8 + "req_pending <= " + str(CHANNEL_NUM) + "`b0;\n")
f.write(' '*4 + "end\n")
f.write(' '*4 + "else begin\n")
f.write(' '*8 + "req_pending <= next_pending;\n")
f.write(' '*4 + "end\n")
f.write("end\n\n")

f.write("endmodule")

f.close()


