module freq_div_and_switch(
  input   wire        clk,      //original clk/fastest clk
  input   wire        rstn,     //negedge asynch reset
  input   wire  [7:0] div,      //divisor
  output  wire        clk_out
);

reg   [8:0]   cnt;              //main counter
reg   [7:0]   div_next;         //update to div when cnt_hits_top
wire  [8:0]   cnt_top;          //counter top
wire          cnt_hits_top;     //indicator cnt==cnt_top
wire  [8:0]   cnt_half;         //counter half
wire          cnt_hits_half;    //indicator cnt==cnt_half
reg           clk_div;          //divided clock

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    div_next[7:0] <= 8'b0;
  end
  else if (cnt_hits_top) begin
    div_next[7:0] <= div[7:0];
  end
end

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    cnt[8:0] <= 9'b1;
  end
  else if (cnt_hits_top) begin
    cnt[8:0] <= 9'b1;
  end
  else begin
    cnt[8:0] <= cnt[8:0] + 1;
  end
end

assign cnt_top[8:0] = {1'b0, div_next[7:0]} + 1;
assign cnt_hits_top = cnt[8:0] == cnt_top[8:0];
assign cnt_half[8:0] = {1'b0, cnt_top[8:1]};
assign cnt_hits_half = cnt[8:0] == cnt_half[8:0];

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    clk_div <= 1'b1;
  end
  else if (cnt_hits_half) begin
    clk_div <= ~clk_div;
  end
  else if (cnt_hits_top) begin
    clk_div <= 1'b1;
  end
end

assign clk_out = (div_next[7:0] == 8'b0) ? clk : clk_div;

endmodule
