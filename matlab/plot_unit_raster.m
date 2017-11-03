%%% Kate Letai
%%% 10-30-17
%%% plot spike traces of individual units. Unit input is given in format:
%%% [well_row, well_col, ele_col, ele_well, neuron)
function plot_unit_raster(electrode_containers, start, stop, unit, stim_times)
 curr_container = electrode_containers(unit(1), unit(2), unit(3), unit(4));
 all_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == unit(5) ...
        );
 in_window = all_times(isbetween(all_times, start, stop));
 y = ones(1,length(in_window));
 ys = ones(1,length(stim_times));
 
 dur = milliseconds(stop-start);
 times = zeros(1,dur);
 milli_times = milliseconds(in_window-start)+1;
 
 for spike = floor(milli_times)
     times(spike) = times(spike)+1;
 end
 
 ac = autocorr(times,1000);
 
 figure();
 plot(stim_times, ys, 'r.'); hold on;
 plot(in_window, y, 'b.'); hold off;
 title(unit);