% Currently set for Plate 113 dmso
function is_cond = check_cond(unit_name)
row_num = unicode2native(unit_name{1}(1)) - 64;
col_num = str2num(unit_name{1}(2));
is_cond = 0;
if col_num <= 2 && row_num <= 2
    is_cond = 1;
%elseif (col_num == 4 || col_num == 5) && row_num == 2
%    is_cond = 1;
end