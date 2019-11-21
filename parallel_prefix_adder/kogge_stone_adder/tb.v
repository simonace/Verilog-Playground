module tb;

initial begin
  $fsdbDumpfile("kogge_stone.fsdb");
  $fsdbDumpvars(0, tb);
end

reg   [7:0]   a_tb;
reg   [7:0]   b_tb;
reg           c0_tb;
wire  [7:0]   cout_tb;

kogge_stone_adder_carry_chain dut(
  .a    (a_tb),
  .b    (b_tb),
  .c0   (c0_tb),
  .c_o  (cout_tb)
);

initial begin
  a_tb <= 8'h00;
  b_tb <= 8'h00;
  c0_tb <= 1'b0;
  #1000;
  a_tb <= 8'hff;
  b_tb <= 8'h00;
  c0_tb <= 1'b0;
  #1000;
  a_tb <= 8'h00;
  b_tb <= 8'hff;
  c0_tb <= 1'b0;
  #1000;
  a_tb <= 8'hff;
  b_tb <= 8'h00;
  c0_tb <= 1'b1;
  #1000;
  a_tb <= 8'h00;
  b_tb <= 8'hff;
  c0_tb <= 1'b1;
  #1000;
  a_tb <= 8'h01;
  b_tb <= 8'h01;
  c0_tb <= 1'b0;
  #1000;
  a_tb <= 8'h20;
  b_tb <= 8'h20;
  c0_tb <= 1'b0;
  #1000;
  a_tb <= 8'h01;
  b_tb <= 8'h03;
  c0_tb <= 1'b1;
  #1000;
  a_tb <= 8'h55;
  b_tb <= 8'haa;
  c0_tb <= 1'b1;
  #1000;
  $finish;
end
endmodule
