# Data Preparation Scripts
This folder contains utility scripts for data engineering, data cleansing, and data preparation tasks.

## rekognition-manifest-file.py
This Python script simplifies the creation of an Amazon Rekognition Custom Labels manifest file from a CSV file. The manifest file is suitable for multi-label image classification.

### Key features:
- **CSV to JSON Lines:** Converts a simple CSV file (image filename, labels) into the required JSON Lines manifest format.
- **Multi-Label Support:** Handles multiple labels per image for multi-label classification.
- **Duplicate Detection**: Automatically detects and reports duplicate image entries.
- **S3 Path Specification**: Allows specifying the S3 path for images, if not included in the CSV.
- **Comma Handling:** Handles filenames that include multiple commas within the name by checking for "100,100", as in my use case, the width and length of the image was always 100x100.

### To use this script:
1. **Prepare the CSV:** For example, I used [the plant doctor dataset from Roboflow](https://public.roboflow.com/object-detection/plantdoc), which includes a train and a test dataset. The test dataset is optional but can help you assess the accuracy of the model.
2. **Run the script:**
```
python rekognition-manifest-file.py --csv_file my_labels.csv --s3_path s3://my-bucket/my-images/
```
3. **Review Duplicates** If the script detects duplicate image entries, it will instruct you to review and update the deduplicated file, then re-run the script.
4. **Upload the Manifest:** Upload the generated `my_labels.manifest` file to S3 and use it to create your Rekognition Custom Labels dataset.
5. **Repeat for Test Data:** Repeat steps 1-4 for the test dataset, if applicable.
5. **Create the Dataset in Amazon Rekognition:** When creating your Rekognition Custom Labels dataset, choose train and test datasets if applicable. Then, choose the option to "Import images labeled by SageMaker Ground Truth" and enter the S3 path where you stored the manifest file.

### Acknowledgement
This script was adapted from the AWS Documentation on [Creating a manifest file from a CSV file](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-csv-manifest.html).

### Other Keywords
image labeling, object detection, training data preparation
