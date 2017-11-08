% Load the sorted .mat file before running.

% Define output path for table.
resp_output_path = ('/home/sean/mea data/15/171030/15_resp_units_custom.csv');

% Divide electrode_containers into conditions
ec0s = electrode_containers([1:3], 1, :, :);
ec5min = [electrode_containers(1:3, 2, :, :), electrode_containers(4:6, 5, :, :)];
ec1hr = [electrode_containers(1:3, 3, :, :)];
ec2hr = electrode_containers(1:3, 4, :, :);
ec6hr = electrode_containers(1:3, 5, :, :);
ec8hr = electrode_containers(1:3, 6, :, :);
ec12hr = electrode_containers(1:3, 7, :, :);
ec18hr = electrode_containers(1:3, 8, :, :);
ec5Hz = electrode_containers(4, [1:4, 6:8], :, :);
ec10Hz = electrode_containers(5, [1:4, 6:8], :, :);
ec20Hz = electrode_containers(6, [1:4, 6:8], :, :);

% Define stimulation start/stop times for each condition
startHz = min(stim_times);
stopHz = max(stim_times);
start5min = stopHz - minutes(5);
start1hr = stopHz - hours(1);
start2hr = stopHz - hours(2);
start6hr = stopHz - hours(6);
start8hr = stopHz - hours(8);
start12hr = stopHz - hours(12);

% find responsive neurons for each condition
[ru0, ac0] = find_responsive(ec0s, startHz, stopHz, 100);
[ru5m, ac5m] = find_responsive(ec5min, start5min, stopHz, 100);
[ru1h, ac1h] = find_responsive(ec1hr, start1hr, stopHz, 100);
[ru2h, ac2h] = find_responsive(ec2hr, start2hr, stopHz, 100);
[ru6h, ac6h] = find_responsive(ec6hr, start6hr, stopHz, 100);
[ru8h, ac8h] = find_responsive(ec8hr, start8hr, stopHz, 100);
[ru12h, ac12h] = find_responsive(ec12hr, start12hr, stopHz, 100);
[ru18h, ac18h] = find_responsive(ec18hr, startHz, stopHz, 100);
[ru5hz, ac5hz] = find_responsive(ec5Hz, startHz, stopHz, 200);
[ru10hz, ac10hz] = find_responsive(ec10Hz, startHz, stopHz, 100);
[ru20hz, ac20hz] = find_responsive(ec20Hz, startHz, stopHz, 50);

% Concatenate all responsive neurons and save to table.
stim_resp = [ru0, ru5m, ru1h, ru2h, ru6h, ru8h, ru12h, ru18h, ru5hz, ru10hz, ru20hz];
autocorr = [ac0, ac5m, ac1h, ac2h, ac6h, ac8h, ac12h, ac18h, ac5hz, ac10hz, ac20hz];
resp_table = table(stim_resp', autocorr', 'VariableNames', {'unit_name', 'autocorr'});
writetable(resp_table, resp_output_path);