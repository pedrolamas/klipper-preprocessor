# Klipper Preprocessor script for Cura

[![Project Maintenance](https://img.shields.io/maintenance/yes/2023.svg)](https://github.com/pedrolamas/klipper-preprocessor 'GitHub Repository')
[![License](https://img.shields.io/github/license/pedrolamas/klipper-preprocessor.svg)](https://github.com/pedrolamas/klipper-preprocessor/blob/master/LICENSE 'License')

[![Follow pedrolamas on Twitter](https://img.shields.io/twitter/follow/pedrolamas?label=Follow%20@pedrolamas%20on%20Twitter&style=social)](https://twitter.com/pedrolamas)
[![Follow pedrolamas on Mastodon](https://img.shields.io/mastodon/follow/109365776481898704?label=Follow%20@pedrolamas%20on%20Mastodon&domain=https%3A%2F%2Fhachyderm.io&style=social)](https://hachyderm.io/@pedrolamas)

`Klipper Preprocessor` is a [Cura](https://ultimaker.com/software/ultimaker-cura) Post Processing Script to improve the output G-Code for [Klipper](https://github.com/Klipper3d/klipper) usage.

Currently it allows the following improvements:

- Add `SET_PRINT_STATS_INFO` so that Klipper can know what is the exact total layer count, and the current layer number in real-time.
- Add `TIMELAPSE_TAKE_FRAME` so that Klipper together with [moonraker-timelapse](https://github.com/mainsail-crew/moonraker-timelapse) can take snapshots on each layer change to make timelapse videos.
- Run [preprocess_cancellation](https://github.com/kageurufu/preprocess_cancellation) tool to add object cancellation data to the resulting G-Code, enabling Klipper to cancel any specific single object while printing.
- Run [klipper_estimator](https://github.com/Annex-Engineering/klipper_estimator) to add a more accurate time estimation to the resulting G-Code.

![Klipper Preprocessor script for Cura](assets/images/Klipper%20Preprocessor%20script%20for%20Cura.png "Klipper Preprocessor script for Cura")

## Initial setup

1. Open Cura
2. Open the "Help" menu and click "Show Configuration Folder"
3. On the file list, open the "scripts" folder
4. Download [KlipperPreprocessor.py](KlipperPreprocessor.py) to the "scripts" folder
5. Close the file list
6. Close Cura
7. (optional) Download [preprocess_cancellation](https://github.com/kageurufu/preprocess_cancellation/releases/latest) to a folder of your choice
8. (optional) Download [klipper_estimator](https://github.com/Annex-Engineering/klipper_estimator/releases/latest) to a folder of your choice
9. Open Cura
10. Open the "Extensions" menu, then "Post Processing", and click on "Modify G-Code"
11. Click on "Add a script" and select "Klipper Preprocessor"
12. Set options acording to your needs (hover any option to view the description)
13. Click "Close" when ready

## Recommended Cura settings for Klipper

Klipper documentation includes some generic [slicer recommended settings](https://www.klipper3d.org/Slicers.html#slicers) that must be followed.

Below are some other settings that will improve your Cura slicing results while using Klipper.

### Disable Jerk

Klipper does not support Jerk and instead relies on [square_corner_velocity](https://www.klipper3d.org/Config_Reference.html#printer).

Is is recommended to untick the "Enable Jerk Control" option in the "Speed" section in Cura.

### Adding extra metadata for Moonraker

Moonraker actively reads metadata from all sliced files, but there is some missing data in Cura sliced files.

To make sure you get all possible metadata on these files, add this to the top of your "Start G-code" in Cura, before any other instructions:

```text
;Nozzle diameter = {machine_nozzle_size}
;Filament type = {material_type}
;Filament name = {material_name}
;Filament weight = {filament_weight}
; M190 S{material_bed_temperature_layer_0}
; M109 S{material_print_temperature_layer_0}
```

These lines are marked as comments, so they have no impact on the g-code, but Moonraker will still be able to find and use those values.

### Improving Cura print time estimations

The default printer (machine) profiles in Cura have fixed values for max-acceleration and max-speed, so when we set values above those defaults while slicing a file, Cura will ignore when estimating the printing time and use the default ones instead, so the estimation will be off.

To fix this, follow these steps:

1. Open Cura
2. Click on the "Marketplace" button on the top right of the window
3. On the Plugins list, select the "Printer Settings"
4. Click "Install"
5. Restart Cura
6. On the "Print settings" flyout, there should now be a new section called "Printer Settings" (you might need to ensure they are visible by clicking the "hamburger" menu on the top right and selecting "All")
7. Expand that section and change the "Maximum Speed..." and "Maximum Acceleration..." fields to match the values you are using in your Klipper configuration

## FAQ

### Why am I seeing "Unknown Command M205" while printing?

That will be because you have jerk enabled in Cura. You can safely [disable jerk](#disable-jerk) to fix it.

### What is the "NOMESH" object?

Cura 5.3 was released with a [bug](https://github.com/Ultimaker/Cura/issues/14679) that causes the identification of a "NOMESH" object.

To mitigate this issue, add a "Search and Replace" post-processing script before any other script, then set the "Search" field to `;MESH:NOMESH`, the "Replace" field to `;MESH:NONMESH` and untick the "Use Regular Expressions" field.

## Credits and Acknowledgements

- [Klipper](https://github.com/Klipper3d/klipper) by [Kevin O'Connor](https://github.com/KevinOConnor)
- [Moonraker](https://github.com/Arksine/moonraker) by [Eric Callahan](https://github.com/Arksine)
- [klipper_estimator](https://github.com/Annex-Engineering/klipper_estimator) by [Lasse Dalegaard](https://github.com/dalegaard)
- [preprocess_cancellation](https://github.com/kageurufu/preprocess_cancellation) by [Frank Tackitt](https://github.com/kageurufu)
- [moonraker-timelapse](https://github.com/mainsail-crew/moonraker-timelapse) by [Mainsail Crew](https://github.com/mainsail-crew)
- [Cura](https://github.com/Ultimaker/Cura) by [UltiMaker](https://github.com/Ultimaker)

## License

MIT
