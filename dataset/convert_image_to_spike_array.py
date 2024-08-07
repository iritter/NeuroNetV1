import numpy as np
import cv2
import sys
import os
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter
from poisson_tools import image_to_poisson_trains
from util_functions import raster_plot_spike, pickle_it

def apply_receptive_field_filter(img, sigma=1):
    """
    Apply a Gaussian filter to the image to simulate the receptive field.
    :param img: Input grayscale image
    :param sigma: Standard deviation for Gaussian kernel
    :return: Filtered image
    """
    return gaussian_filter(img, sigma=sigma)

def img_to_spike_array(img_file_name, max_freq, on_duration, off_duration, sigma=1, save_as_pickle=True, save_plot=True):
    img = cv2.imread(img_file_name, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        height, width = img.shape
        
        print(f"Processing {img_file_name} with shape {img.shape}...")

        # Apply the receptive field filter (Gaussian filter)
        print("Applying Gaussian filter...")
        filtered_img = apply_receptive_field_filter(img, sigma=sigma)
        print("Gaussian filter applied.")
        
        # Flatten the filtered image and convert to spike trains
        print("Converting image to spike trains...")
        spikes = image_to_poisson_trains(np.array([filtered_img.reshape(height * width)]),
                                         height, width,
                                         max_freq, on_duration, off_duration)
        print("Image converted to spike trains.")

        # Save the raster plot
        if save_plot:
            print("Saving raster plot...")
            plot_dir = "raster_plots"
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)

            img_base_name = os.path.basename(img_file_name)
            img_base_name = os.path.splitext(img_base_name)[0]
            plot_file = os.path.join(plot_dir, f"raster_plot_{img_base_name}.png")

            plt.figure()
            raster_plot_spike(spikes, title=f"Raster Plot of {img_base_name}", xlabel="Time (ms)", ylabel="Neuron Index")
            plt.savefig(plot_file)
            plt.close()
            print("Raster plot saved.")

        # Pickle the spike array for further use
        if save_as_pickle:
            print("Saving spike array to pickle...")
            pickle_dir = "pickles_files"
            if not os.path.exists(pickle_dir):
                os.makedirs(pickle_dir)

            img_base_name = os.path.basename(img_file_name)
            img_base_name = os.path.splitext(img_base_name)[0]
            pickle_file = os.path.join(pickle_dir, f"spike_array_{img_base_name}.pkl")
            pickle_it(spikes, pickle_file)
            print("Spike array saved to pickle.")
        
        print(f"Finished processing {img_file_name}.")
    else:
        print(f"Image couldn't be read! -> from file ({img_file_name})")

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 5:
        print("Usage:")
        print("\t python convert_image_to_spike_array.py <img_file_name> <max_freq> <on_duration> <off_duration>")
        print("or (with the default values for up to a 32x32 image {max_freq=1000} {on_duration=200} {off_duration=100}):")
        print("\t python convert_image_to_spike_array.py <img_file_name>")
    else:
        img_file_name = sys.argv[1]

        if len(sys.argv) > 2:
            max_freq = int(sys.argv[2])       # Hz
            on_duration = int(sys.argv[3])    # ms
            off_duration = int(sys.argv[4])   # ms
        else:
            max_freq = 1000      # Hz
            on_duration = 200    # ms
            off_duration = 100   # ms

        print(f"max_freq: {max_freq}")
        print(f"on_duration: {on_duration}")
        print(f"off_duration: {off_duration}")

        if os.path.isdir(img_file_name):
            import glob
            image_list = glob.glob(os.path.join(img_file_name, "*.png"))
            for img in image_list:
                if os.path.isfile(img):
                    img_to_spike_array(img, max_freq, on_duration, off_duration)
        elif os.path.isfile(img_file_name):
            img_to_spike_array(img_file_name, max_freq, on_duration, off_duration)
