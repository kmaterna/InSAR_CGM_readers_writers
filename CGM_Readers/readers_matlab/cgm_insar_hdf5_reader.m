% example script to read the HDF5-formated CGM InSAR products
% by Kang Wang (kwang@seismo.berkeley.edu) in May, 2021
clc
clf
clear

h5= 'D071_COMB_CGM_InSAR_v0_0_1_1Gb.hdf5';%
info=h5info(h5);
%%display the contents of the HDF5 file
%  h5disp(h5);
% Now one can read in the data according to attribute location

%% image size, bounds info etc.
track=info.Groups(2).Name; % track name
topo=h5read(h5,[track,'/Grid_Info/dem'])'; %elevation
topo=flipud(topo);

lat_sar=h5read(h5,[track,'/Grid_Info/lat']); %vector of  latitude
lon_sar=h5read(h5,[track,'/Grid_Info/lon']); %vector of longitude

%% velocity
vlos=h5read(h5,[track,'/Velocities/velocities'])'; %average velocity (mm/yr)
vlos=flipud(vlos);

vE=h5read(h5,[track,'/Grid_Info/lkv_E'])'; % East-component of the unit LOS vector
vE=flipud(vE);
vN=h5read(h5,[track,'/Grid_Info/lkv_N'])'; % North-component of the unit LOS vector
vN=flipud(vN);
vU=h5read(h5,[track,'/Grid_Info/lkv_U'])'; % Up-component of the unit LOS vector
vU=flip(vU);
% LOS displacement = uE*vE + uN*vN +uU*vU, where uE, uN and uU represent the
% Eastward, Northward and Upward motion, respectively.

%% time of the SAR acquisition
nsar=length(h5info(h5,[track,'/Time_Series']).Datasets);%number of SAR acquisitions
for k=1:nsar;
    time_sar{k}=h5info(h5,[track,'/Time_Series']).Datasets(k).Name; %cell containg the SAR image acquisition time
end
day_sar=datenum(time_sar,'yyyymmddTHHMMSS');%time of the SAR acquisition in the unit of days since January 0, 0000;
yr_sar=decyear(datestr(day_sar)); %time of the SAR acquisition in the unit of decimal year

%% load in the InSAR time series;
for k=1:nsar
    dlos_this_sar=h5read(h5,[track,'/Time_Series/',time_sar{k}])';
    dlos{k}=flipud(dlos_this_sar);
end

%%

%% dispaly the results
dx=mean(diff(lon_sar)); %average E-W pixel spacing in degrees
dy=mean(diff(lat_sar)); %average N-S pixel spacing in degrees

% plot the topography
% figure
% h=imagesc(lon_sar,lat_sar,topo);
% set(gca,'YDir','normal');
% axis equal
% colorbar
% colormap(jet);
% set(h,'alphadata',~isnan(vlos));


%%  plot out the velocity
hv=figure(2);
h=imagesc(lon_sar,lat_sar,vlos);
set(gca,'YDir','normal');
axis equal
colorbar
colormap(jet);
caxis([-25 10]);
set(h,'alphadata',~isnan(vlos));

%% check in the time series at a given point
%lon_pt=-118.413;
%lat_pt=34.243;

% or pick a point from the velocity map;
figure(hv);
[lon_pt,lat_pt]=ginput(1);

% for the pixel to examine, average the displacement 6*6 pixels (~1.2km * 1.2 km) around it.
ix=find(lon_sar>=(lon_pt-3*dx)  & lon_sar<=(lon_pt+3*dx)); %pixel index along E-W direction
iy=find(lat_sar>=(lat_pt-3*dy)  & lat_sar<=(lat_pt+3*dy)); %pixel index along N-W direction
dlos_pt=NaN(nsar,1); %vector to hold the LOS displacement at each SAR acquisition time
std_pt=NaN(nsar,1);  %vector to hold the standard deviation at each SAR acquisition time

for k=1:nsar;
    dlos_this_sar=dlos{k};
    dlos_pt_this_sar=dlos_this_sar(iy,ix);
    dlos_pt_good_pixel=dlos_pt_this_sar(~isnan(dlos_pt_this_sar)); %value of good pixels
    dlos_pt(k)=mean(dlos_pt_good_pixel);
    std_pt(k)=std(dlos_pt_good_pixel);
end

figure;
plot(yr_sar,dlos_pt,'k--','LineWidth',1);
hold on
plot(yr_sar,dlos_pt,'o','MarkerSize',6,'MarkerFaceColor','b','MarkerEdgeColor','k','LineWidth',1.5);
errorbar(yr_sar,dlos_pt,std_pt,'r-','LineWidth',1.2);
%error bar standards for the standard deviation of displacement around
%point of interest with respect to its mean; the
xlabel('Time (yr)');
ylabel('dLOS displacement (mm)');

