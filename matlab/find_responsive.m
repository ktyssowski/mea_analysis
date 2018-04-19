%%% Kate Letai
%%% 10-31-17
%%% Checks autocorrelation of each neuron. If a peak occurs at "peak" 
%%% (the # of milliseconds between stimulations), then that neuron is returned
%%% as a light-responding neuron.

function [responding_units, responding_ac] = find_responsive(electrode_containers, start, stop, peak)
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);
dur = milliseconds(stop-start);
 
curr_unit = 1;
responding_units = {};
responding_ac = [];
for curr_container = containers_with_data(:)'
    unit_names = curr_container.get_unit_names();
    for iClust = 1:curr_container.n_clusters
        all_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == iClust ...
        );
        in_window = all_times(isbetween(all_times, start, stop));
 
        times = zeros(1,ceil(dur));
        milli_times = milliseconds(in_window-start)+1;
 
        for spike = floor(milli_times)
            times(spike) = times(spike)+1;
        end
 
        [ac, ~, bounds] = autocorr(times,1000,0,25);
        if ac(peak+1) > bounds(1)
            responding_units = [responding_units, unit_names(iClust)];
            responding_ac = [responding_ac, ac(peak+1)];
        end
        curr_unit = curr_unit+1;
    end
end