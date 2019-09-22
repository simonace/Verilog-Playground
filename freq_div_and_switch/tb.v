module tb;

initial begin
  $fsdbDumpfile("freq_div_and_switch.fsdb");
  $fsdbDumpvars(0,tb);
end

reg     clk_tb;
reg     rstn_tb;
reg [7:0] div_tb;
wire      clk_out_tb;

freq_div_and_switch dut (
  .clk  (clk_tb),
  .rstn (rstn_tb),
  .div  (div_tb),
  .clk_out (clk_out_tb)
);

initial begin
  clk_tb <= 1'b0;
  rstn_tb <= 1'b1;
  div_tb <= 8'b0;
  #1000;
  rstn_tb <= 1'b0;
  #1000;
  rstn_tb <= 1'b1;
  #1000;
  div_tb <= 8'h1;
  #5000;
  div_tb <= 8'h2;
  #5000;
  div_tb <= 8'h5;
  #5000;
  div_tb <= 8'h0;
  #5000;
  $finish;
end

always #100 clk_tb <= ~clk_tb;

endmodule
