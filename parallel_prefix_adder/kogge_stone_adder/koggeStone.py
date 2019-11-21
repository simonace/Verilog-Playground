WIDTH = 8

moduleName = "kogge_stone_adder_carry_chain_" + str(WIDTH) + "_bit_width"

f = open(moduleName + ".v", "w+")

f.write("module " + moduleName + " (\n")
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + ("[" + str(WIDTH-1) + ":0]").ljust(8) + "a".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + ("[" + str(WIDTH-1) + ":0]").ljust(8) + "b".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + "".ljust(8) + "c_in".ljust(8) + ',' + '\n')
f.write(' '*4 + "output".ljust(8) + "wire".ljust(8) + ("[" + str(WIDTH-1) + ":0]").ljust(8) + "c".ljust(8) + '\n')
f.write(");\n")

f.write("\n")
f.write("wire".ljust(8) + ("[" + str(WIDTH-1) + ":0]").ljust(8) + "p".ljust(12) + ";\n")
f.write("wire".ljust(8) + ("[" + str(WIDTH-1) + ":0]").ljust(8) + "g".ljust(12) + ";\n")
pgNetDepth = len(str(bin(WIDTH-1)))-2
for i in range(WIDTH):
    f.write("wire".ljust(8) + "".ljust(8) + ("p_" + str(i) + '_' + str(i)).ljust(12) + ";\n")
    f.write("wire".ljust(8) + "".ljust(8) + ("g_" + str(i) + '_' + str(i)).ljust(12) + ";\n")
for i in range(pgNetDepth):
    indexDistance = 2**i
    for j in range(indexDistance, WIDTH):
        lowerIndex = j-indexDistance*2+1 if (j-indexDistance*2+1)>=0 else 0
        f.write("wire".ljust(8) + "".ljust(8) + ("p_" + str(j) + '_' + str(lowerIndex)).ljust(12) + ";\n")
        f.write("wire".ljust(8) + "".ljust(8) + ("g_" + str(j) + '_' + str(lowerIndex)).ljust(12) + ";\n")
f.write("\n")
f.write("assign p[" + str(WIDTH-1) + ":0] = a[" + str(WIDTH-1) + ":0] ^ b[" + str(WIDTH-1) + ":0];\n")
f.write("assign g[" + str(WIDTH-1) + ":0] = a[" + str(WIDTH-1) + ":0] & b[" + str(WIDTH-1) + ":0];\n")
for i in range(WIDTH):
    f.write("assign p_" + str(i) + '_' + str(i) + " = p[" + str(i) + "];\n")
    f.write("assign g_" + str(i) + '_' + str(i) + " = g[" + str(i) + "];\n")
for i in range(WIDTH):
    f.write("assign c[" + str(i) + "] = g_" + str(i) + "_0 | (p_" + str(i) + "_0 & c_in);\n")

f.write("\n")
for i in range(pgNetDepth):
    indexDistance = 2**i
    for j in range(indexDistance, WIDTH):
        lowerIndex = j-indexDistance*2+1 if (j-indexDistance*2+1)>=0 else 0
        f.write("pg_node u_pg_" + str(j) + '_' + str(lowerIndex) + " (\n")
        middleIndex = j-indexDistance
        f.write(' '*4 + ".pi1".ljust(8) + "(p_" + str(j) + '_' + str(middleIndex+1) + "),\n")
        f.write(' '*4 + ".pi2".ljust(8) + "(p_" + str(middleIndex) + '_' + str(lowerIndex) + "),\n")
        f.write(' '*4 + ".gi1".ljust(8) + "(g_" + str(j) + '_' + str(middleIndex+1) + "),\n")
        f.write(' '*4 + ".gi2".ljust(8) + "(g_" + str(middleIndex) + '_' + str(lowerIndex) + "),\n")
        f.write(' '*4 + ".pout".ljust(8) + "(p_" + str(j) + '_' + str(lowerIndex) + "),\n")
        f.write(' '*4 + ".gout".ljust(8) + "(g_" + str(j) + '_' + str(lowerIndex) + ")\n")
        f.write(");\n\n")
f.write("endmodule\n\n\n")
    
f.write("//sub module: pg_node\n")
f.write("module pg_node (\n")
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + "".ljust(8) + "pi1".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + "".ljust(8) + "pi2".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + "".ljust(8) + "gi1".ljust(8) + ',' + '\n')
f.write(' '*4 + "input".ljust(8) + "wire".ljust(8) + "".ljust(8) + "gi2".ljust(8) + ',' + '\n')
f.write(' '*4 + "output".ljust(8) + "wire".ljust(8) + "".ljust(8) + "pout".ljust(8) + ',' + '\n')
f.write(' '*4 + "output".ljust(8) + "wire".ljust(8) + "".ljust(8) + "gout".ljust(8) + '\n')
f.write("); \n")
f.write("\n"*1)
f.write("assign pout = pi1 & pi2;\n")
f.write("assign gout = gi1 | (pi1 & gi2);\n\n")
f.write("endmodule\n")

f.close()


