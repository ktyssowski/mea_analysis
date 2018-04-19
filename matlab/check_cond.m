% Currently set for Plate 66 dmso
function is_cond = check_cond(unit_name)
row_num = unicode2native(unit_name{1}(1)) - 64;
col_num = str2num(unit_name{1}(2));
is_cond = 0;
if row_num < 4 && col_num == 5
    is_cond = 1;
%elseif row_num >= 4 && col_num == 4
%    is_cond = 1;
end