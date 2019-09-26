module ahb_lite_master_read_write_interface(
  // AHB interface
  input   wire          HCLK,
  input   wire          HRESETn,
  input   wire          HREADY,
  output  wire  [31:0]  HADDR,
  output  wire          HWRITE,
  output  wire  [2:0]   HSIZE,
  output  reg   [31:0]  HWDATA,
  output  wire  [1:0]   HTRANS,

  // read/write instruction fetch interface
  input   wire          instr_available,
  input   wire  [31:0]  instr_haddr,
  input   wire          instr_hwrite,
  input   wire  [2:0]   instr_hsize,
  input   wire  [31:0]  instr_hwdata,

  // hrdata buffer read enable interface
  output  reg           hrdata_ready
);

reg     [31:0]    haddr_pipe_1;
//reg     [31:0]    haddr_pipe_2;
reg               hwrite_pipe_1;
reg               hwrite_pipe_2;
reg     [2:0]     hsize_pipe_1;
reg     [2:0]     hsize_pipe_2;
reg     [31:0]    hwdata_pipe_1;
reg     [31:0]    hwdata_pipe_2;
reg               instr_valid_pipe_1;
reg               instr_valid_pipe_2;

always @(posedge HCLK or negedge HRESETn) begin
  if (~HRESETn) begin
    instr_valid_pipe_1 <= 1'b0;
    instr_valid_pipe_2 <= 1'b0;
    haddr_pipe_1[31:0] <= 32'h0;
    //haddr_pipe_2[31:0] <= 32'h0;
    hwrite_pipe_1 <= 1'b0;
    hwrite_pipe_2 <= 1'b0;
    hwdata_pipe_1[31:0] <= 32'h0;
    hwdata_pipe_2[31:0] <= 32'h0;
    hsize_pipe_1[2:0] <= 3'b0;
    hsize_pipe_2[2:0] <= 3'b0;
    HWDATA[31:0] <= 32'h0;
    hrdata_ready <= 1'b0;
  end
  else if (HREADY) begin
    instr_valid_pipe_1 <= instr_available;
    instr_valid_pipe_2 <= instr_valid_pipe_1;
    haddr_pipe_1[31:0] <= instr_haddr[31:0];
    //haddr_pipe_2[31:0] <= haddr_pipe_1[31:0];        
    hwrite_pipe_1 <= instr_hwrite;
    hwrite_pipe_2 <= hwrite_pipe_1;
    hwdata_pipe_1[31:0] <= instr_hwdata[31:0];
    hwdata_pipe_2[31:0] <= hwdata_pipe_1[31:0];
    hsize_pipe_1[2:0] <= instr_hsize[2:0];
    //hsize_pipe_2[2:0] <= hsize_pipe_1[2:0];
    HWDATA[31:0] <= {32{hwrite_pipe_2}} & hwdata_pipe_2[31:0];
    hrdata_ready <= ~hwrite_pipe_2 & instr_valid_pipe_2;
  end
end

assign HTRANS[1:0] = {instr_valid_pipe_1, 1'b0};
assign HADDR[31:0] = haddr_pipe_1[31:0];
assign HSIZE[2:0] = hsize_pipe_1[2:0];
assign HWRITE = hwrite_pipe_1;

endmodule
