module synch_fifo (
  input   wire              clk,
  input   wire              rstn,
  input   wire              wr_en,
  input   wire              rd_en,
  output  reg   [3:0]       wr_ptr,
  output  reg   [3:0]       rd_ptr,
  output  reg   [3:0]       existed_entries,
  output  reg   [3:0]       available_entries,
  output  reg               full,
  output  reg               empty
);
 
reg   [4:0]     wr_ptr_next;
reg   [4:0]     rd_ptr_next;
wire            wr_round_next;
wire            rd_round_next;
reg             wr_round;
reg             rd_round;
reg   [3:0]     existed_entries_next;
reg   [3:0]     available_entries_next;
reg             full_next;
reg             empty_next;
wire            do_wr;
wire            do_rd;

assign wr_round_next = wr_ptr_next[4];
assign rd_round_next = rd_ptr_next[4];
assign do_wr = wr_en & ~full;
assign do_rd = rd_en & ~empty;

always @(*) begin
  if (do_wr & do_rd) begin
    existed_entries_next <= existed_entries;
    available_entries_next <= available_entries;
    wr_ptr_next[4:0] <= {wr_round, wr_ptr[3:0]} + 1;
    rd_ptr_next[4:0] <= {rd_round, rd_ptr[3:0]} + 1;
  end
  else if (do_wr & ~do_rd) begin
    existed_entries_next <= existed_entries + 1;
    available_entries_next <= available_entries - 1;
    wr_ptr_next[4:0] <= {wr_round, wr_ptr[3:0]} + 1;
    rd_ptr_next[4:0] <= {rd_round, rd_ptr[3:0]};
  end
  else if (~do_wr & do_rd) begin
    existed_entries_next <= existed_entries - 1;
    available_entries_next <= available_entries + 1;
    wr_ptr_next[4:0] <= {wr_round, wr_ptr[3:0]};
    rd_ptr_next[4:0] <= {rd_round, rd_ptr[3:0]} + 1;
  end
  else  begin
    existed_entries_next <= existed_entries;
    available_entries_next <= available_entries;
    wr_ptr_next[4:0] <= {wr_round, wr_ptr[3:0]};
    rd_ptr_next[4:0] <= {rd_round, rd_ptr[3:0]};
  end
end

always @(*) begin
  if (wr_ptr_next[4:0] == rd_ptr_next[4:0]) begin
    full_next <= 1'b0;
    empty_next <= 1'b1;
  end
  else if ((wr_round_next==~rd_round_next) & (wr_ptr_next[3:0]==rd_ptr_next[3:0])) begin
    full_next <= 1'b1;
    empty_next <= 1'b0;
  end
  else begin
    full_next <= 1'b0;
    empty_next <= 1'b0;
  end
end

always @(posedge clk or negedge rstn) begin
  if (~rstn) begin
    full <= 1'b0;
    empty <= 1'b1;
    wr_round <= 1'b0;
    rd_round <= 1'b0;
    wr_ptr[3:0] <= 4'b0;
    rd_ptr[3:0] <= 4'b0;
    existed_entries[3:0] <= 4'h0;
    available_entries[3:0] <= 4'hf;
  end
  else begin
    full <= full_next;
    empty <= empty_next;
    wr_round <= wr_round_next;
    rd_round <= rd_round_next;
    wr_ptr[3:0] <= wr_ptr_next[3:0];
    rd_ptr[3:0] <= rd_ptr_next[3:0];
    existed_entries[3:0] <= existed_entries_next[3:0];
    available_entries[3:0] <= available_entries_next[3:0];
  end
end

endmodule



