##############################################################################
#  SSTMap: A Python library for the calculation of water structure and
#         thermodynamics on solute surfaces from molecular dynamics
#         trajectories.
# MIT License
# Copyright 2016-2017 Lehman College City University of New York and the Authors
#
# Authors: Kamran Haider, Steven Ramsay, Anthony Cruz Balberdy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

import sys
import os
import time
from functools import wraps

import numpy as np
from scipy import stats
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm

##############################################################################
# Utilities
##############################################################################

def function_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print(("Total time running %s: %2.2f seconds" %
               (function.__name__, t1-t0)))
        return result
    return function_timer

def print_progress_bar (count, total):
    """
    Create and update progress bar during a loop.
    
    Parameters
    ----------
    iteration : int
        The number of current iteration, used to calculate current progress. 
    total : int
        Total number of iterations
    
    Notes
    -----
        Based on:
        http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write('Progress |%s| %s%s Done.\r' % (bar, percents, '%'))
    sys.stdout.flush()
    if count == total: 
        print()



def plot_enbr(data_dir, site_indices=None, nbr_norm=False, ref_data=None, ref_nbrs=None):
    """
    Generate an Enbr plot for an arbitrary list of sites. First site should be the reference system.
    sites: a list of keys which represent site labels
    data: a dictionary of sites
    x_values: data points on x-axis
    nbr_norm: Normalize by number of neighbors
    outname: name of output file
    
    Parameters
    ----------
    data_dir : TYPE
        Description
    site_indices : None, optional
        Description
    nbr_norm : bool, optional
        Description
    ref_data : None, optional
        Description
    ref_nbrs : None, optional
        Description
    """
    enbr_files = []
    enbr = {}
    ref_enbr = None
    nbr_files = []
    nbr_values = []

    if not os.path.isdir(data_dir):
        sys.exit(
            "Data directory not found, please check path of the directory again.")

    if site_indices is None:
        enbr_files = [
            f for f in os.listdir(data_dir) if f.endswith("Ewwnbr.txt")]
        if nbr_norm:
            nbr_files = [
                f for f in os.listdir(data_dir) if f.endswith("Nnbrs.txt")]
    else:
        enbr_files = [f for f in os.listdir(data_dir) if f.endswith(
            "Ewwnbr.txt") and int(f[0:3]) in site_indices]
        if nbr_norm:
            nbr_files = [f for f in os.listdir(data_dir) if f.endswith(
                "Nnbrs.txt") and int(f[0:3]) in site_indices]

    for index, file in enumerate(enbr_files):
        site_i = int(file[0:3])
        enbr[site_i] = np.loadtxt(data_dir + "/" + file)
        if nbr_norm:
            nbrs = np.loadtxt(data_dir + "/" + nbr_files[index])
            nbr_values.append(np.sum(nbrs) /nbrs.shape[0])
    if ref_data is not None:
        ref_enbr = np.loadtxt(ref_data)
        if nbr_norm:
            ref_enbr *= ref_nbrs

    for index, site_i in enumerate(enbr.keys()):
        print(("Generating Enbr plot for: ", site_i, enbr_files[index]))
        # Get x and p_x for current site
        site_enbr = enbr[site_i]*0.5
        x_low, x_high = -5.0, 3.0
        enbr_min, enbr_max = np.min(site_enbr), np.max(site_enbr)
        if enbr_min < x_low:
            x_low = enbr_min
        if enbr_max > x_high:
            x_high = enbr_max

        x = np.linspace(x_low, x_high)
        kernel = stats.gaussian_kde(site_enbr)
        p_x = kernel.evaluate(x)
        if nbr_norm:
            site_nbrs = nbr_values[index]
            p_x *= site_nbrs
        # Get x and p_x for reference site, if available
        p_x_ref = None
        if ref_enbr is not None:
            kernel = stats.gaussian_kde(ref_enbr)
            p_x_ref = kernel.evaluate(x)
        # Set up plot
        fig, ax = plt.subplots(1)
        fig.set_size_inches(3, 3)
        plt.xlim(x_low, x_high)
        plt.ylim(0.0, np.max(p_x) + 0.1)
        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(start, end, 0.2))
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(start, end, 2.0))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        x_label = r'$\mathit{E_{n} (kcal/mol)}$'
        y_label = r'$\mathit{\rho(E_{n})}$'
        if nbr_norm:
            y_label = r'$\mathit{\rho(E_{n})N^{nbr}}$'
        ax.set_xlabel(x_label, size=14)
        ax.set_ylabel(y_label, size=14)
        ax.yaxis.tick_left()
        ax.xaxis.tick_bottom()
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        plt.minorticks_on()
        plt.tick_params(which='major', width=1, length=4, direction='in')
        plt.tick_params(which='minor', width=1, length=2, direction='in')
        plt.tick_params(axis='x', labelsize=12)
        plt.tick_params(axis='y', labelsize=12)
        plt.plot(
            x, p_x, antialiased=True, linewidth=1.0, color="red", label=site_i)
        if p_x_ref is not None:
            plt.plot(x, p_x_ref, antialiased=True, linewidth=1.0,
                     color="green", label="Reference")
        fig_name = "%03d_" % site_i
        plt.legend(loc='upper right', prop={'size': 10}, frameon=False)
        plt.tight_layout()
        plt.savefig(data_dir + "/" + fig_name + "Enbr_plot.png", dpi=300)
        plt.close()


def plot_rtheta(data_dir, site_indices=None):

    """
    Parameters
    ----------
    data_dir : TYPE
        Description
    site_indices : None, optional
        Description
    
    """
    rtheta_files = []
    rtheta_data = {}

    print(data_dir)
    if not os.path.isdir(data_dir):
        sys.exit(
            "Data directory not found, please check path of the directory again.")

    if site_indices is None:
        rtheta_files = [
            f for f in os.listdir(data_dir) if f.endswith("r_theta.txt")]
    else:
        rtheta_files = [f for f in os.listdir(data_dir) if f.endswith(
            "r_theta.txt") and int(f[0:3]) in site_indices]

    for index, file in enumerate(rtheta_files):
        site_i = int(file[0:3])
        rtheta_data[site_i] = np.loadtxt(data_dir + "/" + file)

    integ_counts = 16.3624445886
    for index, site_i in enumerate(rtheta_data.keys()):
        print(("Generating r_theta plot for: ", site_i, rtheta_files[index]))
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        theta = rtheta_data[site_i][:, 0]
        r = rtheta_data[site_i][:, 1]
        #Nnbr = len(r)/nwat
        # print nwat, Nnbr
        # generate index matrices
        X, Y = np.mgrid[0:130:131j, 2.0:6.0:41j]
        # generate kernel density estimates
        values = np.vstack([theta, r])
        kernel = stats.gaussian_kde(values)
        positions = np.vstack([X.ravel(), Y.ravel()])
        Z = np.reshape(kernel(positions).T, X.shape)
        Z *= integ_counts*0.1
        #Z /= integ_counts
        sum_counts_kernel = 0
        # print kernel.n
        # correct Z
        for i in range(0, Y.shape[1]):
            d = Y[0, i]
            # get shell_vol
            d_low = d - 0.1
            vol = (4.0 / 3.0) * np.pi * (d**3)
            vol_low = (4.0 / 3.0) * np.pi * (d_low**3)
            shell_vol = vol - vol_low

            counts_bulk = 0.0329*shell_vol
            sum_counts_kernel += np.sum(Z[:, i])
            #Z[:,i] /= counts_bulk
            Z[:, i] = Z[:, i],counts_bulk

        print(sum_counts_kernel)
        legend_label = "%03d_" % site_i
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.5,
                        antialiased=True, alpha=1.0, cmap=cm.coolwarm, label=legend_label)
        x_label = r"$\theta^\circ$"
        y_label = r"$r (\AA)$"
        ax.set_xlabel(x_label)
        ax.set_xlim(0, 130)
        ax.set_ylabel(y_label)
        ax.set_ylim(2.0, 6.0)
        z_label = r'$\mathrm{P(\theta, \AA)}$'
        ax.set_zlabel(z_label)
        #ax.legend(legend_label, loc='upper left', prop={'size':6})
        #ax.set_zlim(0.0, 0.15)
        plt.savefig(data_dir + "/" + legend_label + "rtheta_plot.png", dpi=300)
        plt.close()


def read_hsa_summary(hsa_data_file):
    '''
    Returns a dictionary with hydration site index as keys and a list of various attributes as values.
    Parameters
    ----------
    hsa_data_file : string
        Text file containing 
    
    Returns
    -------
    '''

    f = open(hsa_data_file, 'r')
    data = f.readlines()
    hsa_header = data[0]
    data_keys = hsa_header.strip("\n").split()
    hsa_data = {}
    for l in data[1:]:
        float_converted_data = [float(x) for x in l.strip("\n").split()[1:27]]
        hsa_data[int(l.strip("\n").split()[0])] = float_converted_data
    f.close()
    return hsa_data

def read_gist_summary(gist_data_file):
    '''
    Returns a dictionary with hydration site index as keys and a list of various attributes as values.
    Parameters
    ----------
    hsa_data_file : string
        Text file containing 
    
    Returns
    -------
    '''

    f = open(hsa_data_file, 'r')
    data = f.readlines()
    hsa_header = data[0]
    data_keys = hsa_header.strip("\n").split()
    hsa_data = {}
    for l in data[1:]:
        float_converted_data = [float(x) for x in l.strip("\n").split()[1:27]]
        hsa_data[int(l.strip("\n").split()[0])] = float_converted_data
    f.close()
    return hsa_data

def write_watpdb_from_list(coords, filename, water_id_list, full_water_res=False):
    """Summary
    
    Parameters
    ----------
    traj : TYPE
        Description
    filename : TYPE
        Description
    water_id_list : None, optional
        Description
    wat_coords : None, optional
        Description
    full_water_res : bool, optional
        Description
    
    Returns
    -------
    TYPE
        Description
    """
    pdb_line_format = "{0:6}{1:>5}  {2:<3}{3:<1}{4:>3} {5:1}{6:>4}{7:1}   {8[0]:>8.3f}{8[1]:>8.3f}{8[2]:>8.3f}{9:>6.2f}{10:>6.2f}{11:>12s}\n"
    ter_line_format = "{0:3}   {1:>5}      {2:>3} {3:1}{4:4} \n"
    pdb_lines = []
    # write form the list of (water, frame) tuples
    # at_index, wat in enumerate(water_id_list):
    at = 1
    res = 1
    with open(filename + ".pdb", 'w') as f:
        for i in range(len(water_id_list)):
            wat = water_id_list[i]
            at_index = at #% 10000
            res_index = res % 10000
            #wat_coords = md.utils.in_units_of(
            #    coords[wat[0], wat[1], :], "nanometers", "angstroms")
            wat_coords = coords[wat[0], wat[1], :]
            #chain_id = possible_chains[chain_id_index]
            chain_id = "A"
            pdb_line = pdb_line_format.format(
                "ATOM", at_index, "O", " ", "WAT", chain_id, res_index, " ", wat_coords, 0.00, 0.00, "O")
            #pdb_lines.append(pdb_line)
            f.write(pdb_line)
        
            if full_water_res:
                #H1_coords = md.utils.in_units_of(
                #    coords[wat[0], wat[1] + 1, :], "nanometers", "angstroms")
                H1_coords = coords[wat[0], wat[1] + 1, :]
                pdb_line_H1 = pdb_line_format.format("ATOM", at_index + 1, "H1", " ", "WAT", chain_id, res_index, " ", H1_coords, 0.00, 0.00, "H")
                #pdb_lines.append(pdb_line_H1)
                f.write(pdb_line_H1)
                #H2_coords = md.utils.in_units_of(
                #    coords[wat[0], wat[1] + 2, :], "nanometers", "angstroms")
                H2_coords = coords[wat[0], wat[1] + 2, :]
                pdb_line_H2 = pdb_line_format.format("ATOM", at_index + 2, "H2", " ", "WAT", chain_id, res_index, " ", H2_coords, 0.00, 0.00, "H")
                #pdb_lines.append(pdb_line_H2)
                f.write(pdb_line_H2)
                at += 3
                res += 1
            else:
                at += 1
                res += 1
            if res_index == 9999:
                ter_line = ter_line_format.format(
                    "TER", at, "WAT", chain_id, res_index)
                at = 1
                #pdb_lines.append(ter_line)
    #pdb_lines.append("END")
    #np.savetxt(filename + ".pdb", np.asarray(pdb_lines), fmt="%s")


def write_watpdb_from_coords(filename, coords, full_water_res=False):
    """Summary
    
    Parameters
    ----------
    traj : TYPE
        Description
    filename : TYPE
        Description
    water_id_list : None, optional
        Description
    wat_coords : None, optional
        Description
    full_water_res : bool, optional
        Description
    
    Returns
    -------
    TYPE
        Description
    """

    pdb_line_format = "{0:6}{1:>5}  {2:<3}{3:<1}{4:>3} {5:1}{6:>4}{7:1}   {8[0]:>8.3f}{8[1]:>8.3f}{8[2]:>8.3f}{9:>6.2f}{10:>6.2f}{11:>12s}\n"
    ter_line_format = "{0:3}   {1:>5}      {2:>3} {3:1}{4:4} \n"
    pdb_lines = []
    # write form the list of (water, frame) tuples
    # at_index, wat in enumerate(water_id_list):
    at = 0
    res = 0
    wat_i = 0
    with open(filename + ".pdb", 'w') as f:
        f.write("REMARK Initial number of clusters: N/A\n")
        while wat_i < len(coords):
            at_index = at  # % 10000
            res_index = res % 10000
            # wat_coords = md.utils.in_units_of(
            #    coords[wat[0], wat[1], :], "nanometers", "angstroms")
            wat_coords = coords[wat_i]
            # chain_id = possible_chains[chain_id_index]
            chain_id = "A"
            pdb_line = pdb_line_format.format(
                "ATOM", at_index, "O", " ", "WAT", chain_id, res_index, " ", wat_coords, 0.00, 0.00, "O")
            # pdb_lines.append(pdb_line)
            f.write(pdb_line)
            wat_i += 1
            if full_water_res:
                # H1_coords = md.utils.in_units_of(
                #    coords[wat[0], wat[1] + 1, :], "nanometers", "angstroms")
                H1_coords = coords[wat_i]
                pdb_line_H1 = pdb_line_format.format("ATOM", at_index + 1, "H1", " ", "WAT", chain_id, res_index, " ",
                                                     H1_coords, 0.00, 0.00, "H")
                # pdb_lines.append(pdb_line_H1)
                f.write(pdb_line_H1)
                # H2_coords = md.utils.in_units_of(
                #    coords[wat[0], wat[1] + 2, :], "nanometers", "angstroms")
                H2_coords = coords[wat_i + 1]
                pdb_line_H2 = pdb_line_format.format("ATOM", at_index + 2, "H2", " ", "WAT", chain_id, res_index, " ",
                                                     H2_coords, 0.00, 0.00, "H")
                # pdb_lines.append(pdb_line_H2)
                f.write(pdb_line_H2)
                at += 3
                res += 1
                wat_i += 2
            else:
                at += 1
                res += 1
            if res_index == 9999:
                ter_line = ter_line_format.format("TER", at, "WAT", chain_id, res_index)
                at = 1
                # pdb_lines.append(ter_line)
    # pdb_lines.append("END")
    # np.savetxt(filename + ".pdb", np.asarray(pdb_lines), fmt="%s")

    """
    pdb_line_format = "{0:6}{1:>5}  {2:<3}{3:<1}{4:>3} {5:1}{6:>4}{7:1}   {8[0]:>8.3f}{8[1]:>8.3f}{8[2]:>8.3f}{9:>6.2f}{10:>6.2f}{11:>12s}\n"
    ter_line_format = "{0:3}   {1:>5}      {2:>3} {3:1}{4:4} \n"
    pdb_lines = ["REMARK Initial number of clusters: N/A\n"]
    # write form the list of (water, frame) tuples
    for at in range(len(wat_coords)):
        wat_coord = wat_coords[at]
        at_index = at % 10000
        res_index = at % 10000
        chain_id = "A"
        pdb_line = pdb_line_format.format(
            "ATOM", at_index, "O", " ", "WAT", chain_id, res_index, " ", wat_coord, 0.00, 0.00, "O")
        pdb_lines.append(pdb_line)
        if res_index == 9999:
            ter_line = ter_line_format.format(
                "TER", at_index, "WAT", chain_id, res_index)
            pdb_lines.append(ter_line)
    
    with open(filename + ".pdb", "w") as f:
        f.write("".join(pdb_lines))
    
    """

class GISTFields:
    data_titles = ['index', 'x', 'y', 'z',
                  'N_wat', 'g_O', 'g_H',
                  'TS_tr_dens', 'TS_tr_norm',
                  'TS_or_dens', 'TS_or_norm',
                  'dTSsix-dens', 'dTSsix_norm',
                  'E_sw_dens', 'E_sw_norm', 'E_ww_dens', 'Eww_norm',
                  'E_ww_nbr_dens', 'E_ww_nbr_norm',
                  'N_nbr_dens', 'N_nbr_norm',
                  'f_hb_dens', 'f_hb_norm',
                  'N_hb_sw_dens', 'N_hb_sw_norm', 'N_hb_ww_dens', 'N_hb_ww_norm',
                  'N_don_sw_dens', 'N_don_sw_norm', 'N_acc_sw_dens', 'N_acc_sw_norm',
                  'N_don_ww_dens', 'N_don_ww_norm', 'N_acc_ww_dens', 'N_acc_ww_norm']
    index = 0
    x = 1
    y = 2
    z = 3
    N_wat = 4
    g_O = 5
    g_H = 6
    TS_tr_dens = 7
    TS_tr_norm = 8
    TS_or_dens = 9
    TS_or_norm = 10
    dTSsix_dens = 11
    dTSsix_norm = 12
    E_sw_dens = 13
    E_sw_norm = 14
    E_ww_dens = 15
    Eww_norm = 16
    E_ww_nbr_dens = 17
    E_ww_nbr_norm = 18
    N_nbr_dens = 19
    N_nbr_norm = 20
    f_hb_dens = 21
    f_hb_norm = 22
    N_hb_sw_dens = 23
    N_hb_sw_norm = 24
    N_hb_ww_dens = 25
    N_hb_ww_norm = 26
    N_don_sw_dens = 27
    N_don_sw_norm = 28
    N_acc_sw_dens = 29
    N_acc_sw_norm = 30
    N_don_ww_dens = 31
    N_don_ww_norm = 32
    N_acc_ww_dens = 33
    N_acc_ww_norm = 34

class HSAFields:
    data_titles = ['index', 'x', 'y', 'z',
                  'N_wat', 'g_O', 'g_H',
                  'TS_tr_dens', 'TS_tr_norm',
                  'TS_or_dens', 'TS_or_norm',
                  'dTSsix-dens', 'dTSsix_norm',
                  'E_sw_dens', 'E_sw_norm', 'E_ww_dens', 'Eww_norm',
                  'E_ww_nbr_dens', 'E_ww_nbr_norm',
                  'N_nbr_dens', 'N_nbr_norm',
                  'f_hb_dens', 'f_hb_norm',
                  'N_hb_sw_dens', 'N_hb_sw_norm', 'N_hb_ww_dens', 'N_hb_ww_norm',
                  'N_don_sw_dens', 'N_don_sw_norm', 'N_acc_sw_dens', 'N_acc_sw_norm',
                  'N_don_ww_dens', 'N_don_ww_norm', 'N_acc_ww_dens', 'N_acc_ww_norm']
    index = 0
    x = 1
    y = 2
    z = 3
    nwat = 4
    occupancy = 5
    Esw = 6
    EswLJ = 7
    EswElec = 8
    Eww = 9
    EwwLJ = 10
    EwwElec = 11
    Etot = 12
    Ewwnbr = 13
    TSsw_trans = 14
    TSsw_orient = 15
    TStot = 16
    Nnbrs = 17
    Nhbww = 18
    Nhbsw = 19
    Nhbtot = 20
    f_hb_ww = 21
    f_enc = 22
    Acc_ww = 23
    Don_ww = 24
    Acc_sw = 25
    Don_sw = 26
    solute_acceptors = 27
    solute_donors = 28
