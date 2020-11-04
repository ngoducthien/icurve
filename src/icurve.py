import matplotlib.pyplot as plt
from scipy import interpolate
import pandas as pd
import numpy as np
import argparse
import datetime
import sys
import os

parser = argparse.ArgumentParser()

parser.add_argument(
    '-f', '-file', '--filename',
    help="Filename",
    dest='filename',
    type=str,
    nargs='*',
    required=True
)

parser.add_argument(
    '-s', '-skip', '--skiprows',
    help="Number of lines to skip at the start of the file.",
    dest='skiprows',
    type=int,
    nargs=1,
    required=True
)

parser.add_argument(
    '-xmin', '--xmin',
    help="Minimum value of x-axis for interpolation.",
    dest='xmin',
    type=float,
    nargs=1,
    required=True
)

parser.add_argument(
    '-xmax', '--xmax',
    help="Maximum value of x-axis for interpolation.",
    dest='xmax',
    type=float,
    nargs=1,
    required=True
)

parser.add_argument(
    '-n', '--npoints',
    help="Number of points for interpolation.",
    dest='npoints',
    type=int,
    nargs=1,
    required=True
)

parser.add_argument(
    '-k', '--kind',
    help="Specifies the interpolation method. \
          Options: linear, nearest, zero, slinear, \
                   quadratic, cubic, previous, ‘next.",
    dest='kind',
    type=str,
    nargs=1,
    required=False,
    default=['linear']
)

parser.add_argument(
    '-p', '--plot',
    help="Plot the raw data vs. interpolated data.\
            Default: No;\
            Options: Yes, True, 1, No, False, 0",
    dest='plot',
    type=str,
    nargs=1,
    required=False,
    default=['No']
)

args = parser.parse_args()

filename = args.filename[0]
skiprows = args.skiprows[0]
xmin = args.xmin[0]
xmax = args.xmax[0]
npoints = args.npoints[0]
kind = args.kind[0]
plot = args.plot[0]

# Extracting extension from filename
file, file_extension = os.path.splitext(filename)

# Output files
output_file = '{0}_interp{1}'.format(file, file_extension)
log_file = '{0}_interp.log'.format(file)
fig_file = '{0}_interp_plot.png'.format(file)

# Loading the DataFrame from source
if '.csv' in filename.lower():
    data = pd.read_csv(filename, skiprows=skiprows, header=None)
else:
    data = pd.read_csv(filename, sep=r'\s+', skiprows=skiprows, header=None)

# print(data.head())

# The number of columns in the DataFrame
ncols = len(data.columns)

x0_raw = data[0]
x0_min = np.min(x0_raw)
x0_max = np.max(x0_raw)

if xmin < x0_min or xmax > x0_max:
    print('ValueError.')
    print('The interpolation range must be in range ({0:.8f}, {1:8f})'.format(
        x0_min, x0_max)
    )
    print('Input value: xmin = {0}, xmax = {1}'.format(
        xmin, xmax)
    )
    sys.exit("Stop Execution.")

if npoints < 3:
    print('ValueError: npoints must be greater than 3.')
    print('Input value: {0}'.format(npoints))
    sys.exit("Stop Execution.")

# Generating new interpolated values for x-axis
x_interp = np.linspace(xmin, xmax, npoints)

# Interpolating curve
data_interp = pd.DataFrame()
data_interp[0] = x_interp

for i in range(1, ncols):
    f = interpolate.interp1d(x0_raw, data[i], kind=kind)
    data_interp[i] = f(x_interp)

# print(data_interp.head())

if plot[0].lower() in ['y', 't', '1']:
    plt.figure(0)
    plt.xlim([xmin, xmax])
    plt.xlabel('x-axis')
    plt.ylabel('y-axis')
    for i in range(1, ncols):
        plt.plot(x0_raw, data[i], 's', label='(col. {0}) Raw Data'.format(i))
        plt.plot(
            x_interp, data_interp[i], '.-',
            label='(col. {0}) Interp. Data'.format(i)
        )
    plt.legend(frameon=False)
    plt.savefig(fig_file)
    # plt.show()

# Save the interpolated DataFrame to output file
if '.csv' in filename.lower():
    np.savetxt(output_file, data_interp, delimiter=",", fmt='%.8f')
else:
    np.savetxt(output_file, data_interp, delimiter=" ", fmt='%.8f')

execution_time = datetime.datetime.now()

# Save the details to the log file
target = open(log_file, 'w')
target.write('{}\n\n'.format(str(args)))
target.write('            Filename : {}\n'.format(filename))
target.write('      x0_min, x0_max : {0:.8f}, {1:.8f}\n'.format(x0_min, x0_max))
target.write('              Output : {}\n'.format(output_file))
target.write('            Log file : {}\n'.format(log_file))
target.write('   Number of columns : {}\n'.format(ncols))
target.write('            Skip row : {}\n'.format(skiprows))
target.write('               x_min : {}\n'.format(xmin))
target.write('               x_max : {}\n'.format(xmax))
target.write('Number of the points : {}\n'.format(npoints))
target.write('Interpolation method : {}\n'.format(kind))
target.write('         Plot figure : {}\n'.format(plot))
target.write('      Execution time : {}\n'.format(execution_time))
target.write('             Version : 1.0 (2020-11-01)\n')
target.close()
