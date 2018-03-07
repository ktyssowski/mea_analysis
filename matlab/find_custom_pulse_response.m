% Load the sorted .mat file before running.

% Define output path for table.
resp_output_path = ('/home/sean/mea data/KelseyL12/L12_resp_units_custom_171116.csv');

% Divide electrode_containers into conditions
ec1Hz = electrode_containers(1, :, :, :);
ec2Hz = electrode_containers(2, :, :, :);
ec0 = electrode_containers(3, :, :, :);
ec5Hz = electrode_containers(4, :, :, :);
ec10Hz = electrode_containers(5, :, :, :);
ec20Hz = electrode_containers(6, :, :, :);

% Define stimulation start/stop times for each condition
startHz = min(stim_times);
stopHz = startHz + seconds(30) + minutes(56) + hours(10);

% find responsive neurons for each condition
[ru0, ac0] = find_responsive(ec0, startHz, stopHz, 100);
[ru1hz, ac1hz] = find_responsive(ec1Hz, startHz, stopHz, 1000);
[ru2hz, ac2hz] = find_responsive(ec2Hz, startHz, stopHz, 500);
[ru5hz, ac5hz] = find_responsive(ec5Hz, startHz, stopHz, 200);
[ru10hz, ac10hz] = find_responsive(ec10Hz, startHz, stopHz, 100);
[ru20hz, ac20hz] = find_responsive(ec20Hz, startHz, stopHz, 50);

% Concatenate all responsive neurons and save to table.
stim_resp = [ru0, ru1hz, ru2hz, ru5hz, ru10hz, ru20hz];
autocorr = [ac0, ac1hz, ac2hz, ac5hz, ac10hz, ac20hz];
resp_table = table(stim_resp', autocorr', 'VariableNames', {'unit_name', 'autocorr'});
writetable(resp_table, resp_output_path);