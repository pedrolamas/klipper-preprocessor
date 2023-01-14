# Klipper Preprocessor script for Cura

[![Project Maintenance](https://img.shields.io/maintenance/yes/2024.svg)](https://github.com/pedrolamas/klipper-preprocessor 'GitHub Repository')
[![License](https://img.shields.io/github/license/pedrolamas/klipper-preprocessor.svg)](https://github.com/pedrolamas/klipper-preprocessor/blob/master/LICENSE 'License')

[![Follow pedrolamas on Twitter](https://img.shields.io/twitter/follow/pedrolamas?label=Follow%20@pedrolamas%20on%20Twitter&style=social)](https://twitter.com/pedrolamas)
[![Follow pedrolamas on Mastodon](https://img.shields.io/mastodon/follow/109365776481898704?label=Follow%20@pedrolamas%20on%20Mastodon&domain=https%3A%2F%2Fhachyderm.io&style=social)](https://hachyderm.io/@pedrolamas)

`Klipper Preprocessor` is a Cura Post Processing Script to improve the output G-Code for [Klipper](https://github.com/Klipper3d/klipper) usage.

Currently it allows the following improvements:

- Add `SET_PRINT_STATS_INFO` so that Klipper can know what is the exact total layer count, and the current layer number in real-time.
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

## Credits and Acknowledgements

- [Klipper](https://github.com/Klipper3d/klipper) by [Kevin O'Connor](https://github.com/KevinOConnor)
- [Moonraker](https://github.com/Arksine/moonraker) by [Eric Callahan](https://github.com/Arksine)
- [klipper_estimator](https://github.com/Annex-Engineering/klipper_estimator) by [Dalegaard](https://github.com/dalegaard)
- [preprocess_cancellation](https://github.com/kageurufu/preprocess_cancellation) by [Frank Tackitt](https://github.com/kageurufu)

## License

MIT
