import os
from tkinter import filedialog
from PySide6 import QtWidgets, QtCore, QtGui
from PIL import Image
import numpy as np
import tifffile as tfl
import tifftools as tft
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.patches import Rectangle

from define_rectangle import DefineRectangle

class ProcessImage:

    def __init__(self):
        self.arrays = {}
        self.drs = []
        self.mu_dict = {}
        self.phil_dict = {}
        self.images_1p = []
        self.images_2p = []
        self.images_3pE1 = []
        self.images_3pE2 = []
        self.sat_arrays = {}
        self.sat_arrays3p = {}
        self.coord = {0:[500, 1200, 100, 100],1:[500, 1100, 100, 100],2:[500, 1000, 100, 100]}

    def load_image(self, angle, urls, mult_core=1.0, mult_time=1.0):
        x0 = self.coord[1][0]
        y0 = self.coord[1][1]
        x1 = x0 + self.coord[1][2]
        y1 = y0 + self.coord[1][3]
        
        for url in urls:
            name, ext = os.path.splitext(os.path.basename(url))
            
            # --- CORRECTION MAESTRO : Lecture de la vraie image ---
            try:
                imgTft = tft.read_tiff(url)
                nbPage = len(imgTft['ifds'])
                del imgTft
            except Exception:
                nbPage = 1

            if nbPage == 1:
                array = tfl.imread(url)
            elif nbPage == 2:
                array = tfl.imread(url, key=1) # Page 1 = Vraie image
            else:
                # OPTIMISATION 16 BITS : Lecture directe en float16
                arrayTmp = tfl.imread(url, key=range(1, nbPage)).astype(np.float16)
                nbImg, nbRow, nbColumn = arrayTmp.shape
                array = np.zeros((nbRow, nbColumn), dtype=np.float16)
                for i in range(nbImg):
                    array += arrayTmp[i] / nbImg
                del arrayTmp

            # --- CORRECTION RGB : Forcer en Noir & Blanc ---
            array = np.squeeze(array)
            if array.ndim >= 3:
                array = array[:, :, 0] if array.shape[-1] in [3, 4] else array[0, :, :]

            # --- OPTIMISATION 16 BITS (Remplace le 32 bits) ---
            if array.dtype != np.float16:
                array = array.astype(np.float16)

            # --- ROTATION SANS ROGNAGE ---
            array = np.flipud(array)
            k = int(angle // 90)
            if k != 0:
                array = np.rot90(array, k=k)

            # --- MULTIPLICATEURS AVEC PROTECTION DES LIMITES ---
            H, W = array.shape
            y0_s, y1_s = max(0, min(y0, H)), max(0, min(y1, H))
            x0_s, x1_s = max(0, min(x0, W)), max(0, min(x1, W))

            if y0_s < y1_s and x0_s < x1_s:
                array_mult = np.multiply(array[y0_s:y1_s, x0_s:x1_s], mult_time/mult_core)
                array[y0_s:y1_s, x0_s:x1_s] = array_mult

            array = np.multiply(array, mult_core)
            self.arrays[name] = array
            
        return self.arrays

    def create_canvas(self):
        self.fig_img, self.ax_img = plt.subplots()
        self.canvas = FigureCanvas(self.fig_img)
        drs = self._create_rect()
        return True

    def _create_rect(self):
        color = ['r', 'g', 'b']
        for nb in range(len(self.coord)):
            rect = Rectangle((self.coord[nb][0],self.coord[nb][1]),self.coord[nb][2],self.coord[nb][3],
                linewidth=1,edgecolor=color[nb],facecolor='None')
            dr = DefineRectangle(rect)
            self.ax_img.add_patch(dr.rect)
            self.drs.append(dr)
            dr.connect()
        return self.drs

    def get_coordinates(self):
        i=0
        for dr in self.drs:
            x0, y0 = dr.rect.get_xy()
            x0 = int(round(x0))
            y0 = int(round(y0))
            width = int(round(dr.rect.get_width()))
            height = int(round(dr.rect.get_height()))
            self.coord[i] = [x0, y0, width, height]
            i+=1

    def set_loaded_coordinates(self, coord):
        i = 0
        for dr in self.drs:
            dr.rect.set_x(coord[str(i)][0])
            dr.rect.set_y(coord[str(i)][1])
            dr.rect.set_width(coord[str(i)][2])
            dr.rect.set_height(coord[str(i)][3])
            i += 1

    def core_rect(self, name):
        """ PROTECTION ZeroDivisionError ajoutée """
        c = self.coord[0]
        H, W = self.arrays[name].shape
        y0, y1 = max(0, min(c[1], H)), max(0, min(c[1]+c[3], H))
        x0, x1 = max(0, min(c[0], W)), max(0, min(c[0]+c[2], W))
        arr = self.arrays[name][y0:y1, x0:x1]
        if arr.size == 0: return np.ones((5, 5), dtype=np.float16)
        return arr

    def mu_rect(self, name):
        """ PROTECTION ZeroDivisionError ajoutée """
        c = self.coord[2]
        H, W = self.arrays[name].shape
        y0, y1 = max(0, min(c[1], H)), max(0, min(c[1]+c[3], H))
        x0, x1 = max(0, min(c[0], W)), max(0, min(c[0]+c[2], W))
        arr = self.arrays[name][y0:y1, x0:x1]
        if arr.size == 0: return np.ones((5, 5), dtype=np.float16)
        return arr

    def _time_correction(self, ref, img):
        c = self.coord[1]
        H_r, W_r = self.arrays[ref].shape
        y0_r, y1_r = max(0, min(c[1], H_r)), max(0, min(c[1]+c[3], H_r))
        x0_r, x1_r = max(0, min(c[0], W_r)), max(0, min(c[0]+c[2], W_r))
        ref_array = self.arrays[ref][y0_r:y1_r, x0_r:x1_r]
        
        H_i, W_i = self.arrays[img].shape
        y0_i, y1_i = max(0, min(c[1], H_i)), max(0, min(c[1]+c[3], H_i))
        x0_i, x1_i = max(0, min(c[0], W_i)), max(0, min(c[0]+c[2], W_i))
        img_array = self.arrays[img][y0_i:y1_i, x0_i:x1_i]
        
        ref_avg = np.average(ref_array) if ref_array.size > 0 else 1.0
        img_avg = np.average(img_array) if img_array.size > 0 else 1.0
        return ref_avg / img_avg if img_avg != 0 else 1.0

    def compute_mu(self, dry, fluid, diameter):
        time_corr = self._time_correction(dry, fluid)
        c = self.coord[2]
        dry_mu = self.arrays[dry][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        fluid_mu = self.arrays[fluid][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        fluid_corr = fluid_mu * time_corr
        return np.log(np.divide(dry_mu, fluid_corr)) / diameter

    def compute_phil(self, dry, wet, mu):
        time_corr = self._time_correction(dry, wet)
        c = self.coord[0]
        dry_phil = self.arrays[dry][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        wet_phil = self.arrays[wet][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        wet_corr = wet_phil * time_corr
        return np.log(np.divide(dry_phil, wet_corr)) / mu

    def compute_2sat(self, img_name, ref_name, timeref_name, phil_name, phil_type, muref_name, muoil_name, muinj_name, swi):
        time_corr_img = self._time_correction(timeref_name, img_name)
        time_corr_ref = self._time_correction(timeref_name, ref_name)
        c = self.coord[0]
        img_crop = self.arrays[img_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        img_corr = img_crop * time_corr_img
        ref_crop = self.arrays[ref_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        ref_corr = ref_crop * time_corr_ref
        muref = np.average(self.mu_dict[muref_name])
        muoil = np.average(self.mu_dict[muoil_name])
        muinj = np.average(self.mu_dict[muinj_name])
        if type(swi) == str:
            swi = 1 - self.sat_arrays[swi]
        if phil_type == 1:
            phil = np.average(self.phil_dict[phil_name])
        else:
            phil = self.phil_dict[phil_name]
        
        soi_corr = np.divide((1.0 - swi)*(muref - muoil) + muinj - muref, muinj - muoil)
        so = soi_corr + np.divide(np.log(np.divide(img_corr, ref_corr)), np.multiply(phil, (muinj - muoil)))

        so_std = np.std(so)
        so_mean = np.mean(so)
        outliers_min = so_mean-3*so_std
        outliers_max = so_mean+3*so_std
        outliers_mask_min = so < outliers_min
        outliers_mask_max = so > outliers_max
        outliers_mask = outliers_mask_min + outliers_mask_max
        out_pos = np.where(outliers_mask)
        for i in range(len(out_pos[0])):
            if out_pos[0][i]>0 and out_pos[1][i]>0:
                mask = outliers_mask[out_pos[0][i]-1:out_pos[0][i]+2, out_pos[1][i]-1:out_pos[1][i]+2]
                subarray = so[out_pos[0][i]-1:out_pos[0][i]+2, out_pos[1][i]-1:out_pos[1][i]+2] * (1-mask)
                subarray = np.delete(subarray, 4)
                subarray_avg = np.average(subarray)
                so[out_pos[0][i],out_pos[1][i]] = subarray_avg

        return so

    def compute_3sat(self, imgE1_name, imgE2_name, refE1_name, refE2_name, timerefE1_name, timerefE2_name, philE1_name, philE2_name, 
        phil_type, murefE1, murefE2, muoilE1, muoilE2, muoilrefE1, muoilrefE2, mugasE1, mugasE2, swi):
        mu_matrix = np.zeros((3,3), dtype=np.float16)
        img_matrix = np.zeros((3,1), dtype=np.ndarray)
        time_corr_imgE1 = self._time_correction(timerefE1_name, imgE1_name)
        time_corr_imgE2 = self._time_correction(timerefE2_name, imgE2_name)
        time_corr_refE1 = self._time_correction(timerefE1_name, refE1_name)
        time_corr_refE2 = self._time_correction(timerefE2_name, refE2_name)
        c = self.coord[0]
        imgE1_crop = self.arrays[imgE1_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        imgE2_crop = self.arrays[imgE2_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        imgE1_corr = imgE1_crop * time_corr_imgE1
        imgE2_corr = imgE2_crop * time_corr_imgE2
        refE1_crop = self.arrays[refE1_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        refE2_crop = self.arrays[refE2_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        refE1_corr = refE1_crop * time_corr_refE1
        refE2_corr = refE2_crop * time_corr_refE2
        
        if type(swi) == str:
            swi = 1 - self.sat_arrays[swi]
        if phil_type == 1:
            philE1 = np.average(self.phil_dict[philE1_name])
            philE2 = np.average(self.phil_dict[philE2_name])
        else:
            philE1 = self.phil_dict[philE1_name]
            philE2 = self.phil_dict[philE2_name]
        
        mu_matrix[0][0] = muoilE1
        mu_matrix[0][1] = murefE1
        mu_matrix[0][2] = mugasE1
        mu_matrix[1][0] = muoilE2
        mu_matrix[1][1] = murefE2
        mu_matrix[1][2] = mugasE2
        mu_matrix[2] = [1.0, 1.0, 1.0]

        quotientE1 = np.log(np.divide(imgE1_corr, refE1_corr))
        quotientE2 = np.log(np.divide(imgE2_corr, refE2_corr))

        a = np.multiply(muoilrefE1, (1-swi)) + np.multiply(murefE1, swi)-np.divide(quotientE1, philE1)
        b = np.multiply(muoilrefE2, (1-swi)) + np.multiply(murefE2, swi)-np.divide(quotientE2, philE2)
        img_matrix[0][0] = a
        img_matrix[1][0] = b
        img_matrix[2][0] = 1.0

        mu_inv = np.linalg.inv(mu_matrix)
        sat_matrix = mu_inv.dot(img_matrix)

        return sat_matrix[0][0], sat_matrix[1][0]  

    def compute_dmu(self, img_name, ref_name, timeref_name, phil_name, phil_type, swi, muref_name, so_target, process):
        time_corr_img = self._time_correction(timeref_name, img_name)
        time_corr_ref = self._time_correction(timeref_name, ref_name)
        c = self.coord[0]
        img_crop = self.arrays[img_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        img_corr = img_crop * time_corr_img
        ref_crop = self.arrays[ref_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        ref_corr = ref_crop * time_corr_ref
        if type(swi) == str:
            swi = 1 - self.sat_arrays[swi]
        if phil_type == 1:
            phil = np.average(self.phil_dict[phil_name])
        else:
            phil = self.phil_dict[phil_name]
        
        B = np.divide(np.log(np.divide(img_corr, ref_corr)), phil)
        if process == 1:
            a = 1.0
            b_array = np.divide(B, (so_target - (1.0-swi)))
            b = np.average(b_array)
        else:
            muref = np.average(self.mu_dict[muref_name])
            swi_avg = float(np.average(swi))
            a = round((1.0-swi_avg-so_target)/(1.0-so_target), 3)
            b_array = np.divide(np.multiply(muref, swi) - B, (1.0-so_target))
            b = round(np.average(b_array), 3)

        return a, b

    def compute_muoil(self, imgE1_name, imgE2_name, refE1_name, refE2_name, timerefE1_name, timerefE2_name, 
        philE1_name, philE2_name, phil_type, murefE1, murefE2, muoilrefE1, muoilrefE2, swi, so_target, sw_target):
        time_corr_imgE1 = self._time_correction(timerefE1_name, imgE1_name)
        time_corr_imgE2 = self._time_correction(timerefE2_name, imgE2_name)
        time_corr_refE1 = self._time_correction(timerefE1_name, refE1_name)
        time_corr_refE2 = self._time_correction(timerefE2_name, refE2_name)
        c = self.coord[0]
        imgE1_crop = self.arrays[imgE1_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        imgE2_crop = self.arrays[imgE2_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        imgE1_corr = imgE1_crop * time_corr_imgE1
        imgE2_corr = imgE2_crop * time_corr_imgE2
        refE1_crop = self.arrays[refE1_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        refE2_crop = self.arrays[refE2_name][c[1]:c[1]+c[3], c[0]:c[0]+c[2]]
        refE1_corr = refE1_crop * time_corr_refE1
        refE2_corr = refE2_crop * time_corr_refE2
        if type(swi) == str:
            swi = 1 - self.sat_arrays[swi]
        if phil_type == 1:
            philE1 = np.average(self.phil_dict[philE1_name])
            philE2 = np.average(self.phil_dict[philE2_name])
        else:
            philE1 = self.phil_dict[philE1_name]
            philE2 = self.phil_dict[philE2_name]

        B1 = np.divide(np.log(np.divide(imgE1_corr, refE1_corr)), philE1)
        B2 = np.divide(np.log(np.divide(imgE2_corr, refE2_corr)), philE2)

        muoilE1_array = (murefE1*(swi-sw_target) + muoilrefE1*(1-swi)+B1)*(1/so_target)
        muoilE2_array = (murefE2*(swi-sw_target) + muoilrefE2*(1-swi)+B2)*(1/so_target)
        muoilE1 = round(np.average(muoilE1_array), 3)
        muoilE2 = round(np.average(muoilE2_array), 3)

        return muoilE1, muoilE2

    def compute_percentile(self, muref_name, muoil_name):
        muref_array = self.mu_dict[muref_name]
        muoil_array = self.mu_dict[muoil_name]
        percentiles_nb = np.arange(0, 101, 1)
        p_muref = np.percentile(muref_array, percentiles_nb)
        p_muoil = np.percentile(muoil_array, percentiles_nb)
        mean_ref = np.average(muref_array)
        sigma_ref = np.std(muref_array)
        mean_oil = np.average(muoil_array)
        sigma_oil = np.std(muoil_array)
        return p_muref, p_muoil, mean_ref, sigma_ref, mean_oil, sigma_oil

    def check_percentile(self, p_muref, p_muoil, muwater, muoil):
        idx_water = np.abs(p_muref - muwater).argmin()
        idx_oil = np.abs(p_muoil - muoil).argmin()
        return idx_water, idx_oil