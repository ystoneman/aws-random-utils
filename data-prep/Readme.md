# Data Preparation Scripts
This folder contains utility scripts for data engineering, data cleansing, and data preparation tasks.

## rekognition-manifest-file.py
This Python script simplifies the creation of an Amazon Rekognition Custom Labels manifest file from a CSV file. The manifest file is suitable for multi-label image classification.

### Key features:
- Converts a simple CSV file (image filename, labels) into the required JSON Lines manifest format
- Handles multiple labels per image for multi-label classification
- Automatically detects and reports duplicate image entries
- Allows specifying the S3 path for images, if not included in the CSV
- Handles filenames that include multiple commas within the name. However, it does this by checking for "100,100" because in my use case, the width and length of the image was always 100 and 100.

### Acknowledgement
This was adapted for my needs from the AWS Documentation on [Creating a manifest file from a CSV file](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-csv-manifest.html).

### Keywords
Amazon Rekognition Custom Labels, manifest file, CSV to JSON, image labeling, multi-label classification, object detection, training data preparation

### To use this script:
1. Get your CSV file. For this use case, I used [the plant doctor dataset from Roboflow](https://public.roboflow.com/object-detection/plantdoc).
2. Run the script, specifying the CSV file and optionally the S3 path for the images:
```
python rekognition-manifest-file.py --csv_file my_labels.csv --s3_path s3://my-bucket/my-images/
```
3. If the script detects duplicate image entries, it will instruct you to review and update the deduplicated file, then re-run the script.
4. Upload the generated `my_labels.manifest` file to S3 and use it to create your Rekognition Custom Labels dataset.
5. When creating your Rekognition Custom Labels dataset, choose the option to "Import images labeled by SageMaker Ground Truth" and enter the S3 path where you stored the manifest file.
